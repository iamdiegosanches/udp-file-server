import socket
import threading
import os
import json

HOST = 'ip'
PORT = 2003
BUFFER_SIZE = 1024 * 5
UPLOAD_PASSWORD = "senha"
FILES_DIR = "files" # alterar isso aqui

os.makedirs(FILES_DIR, exist_ok=True)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def list_files():
    try:
        return dict(enumerate(os.listdir(FILES_DIR)))
    except Exception as e:
        print("Erro ao ler arquivos: ", e)
        return {}

def send_file(index, addr, sock):
    files = list_files()
    name =  files.get(int(index))

    if name:
        sock.sendto(name.encode(), addr)

        try:
            with open(os.path.join(FILES_DIR, name), 'rb') as f:
                while (chunk := f.read(BUFFER_SIZE)):
                    sock.sendto(chunk, addr)
            sock.sendto(chunk, addr)
            print(f"[+] Arquivo '{name}' enviado para {addr}")
        except Exception as e:
            print("Erro ao abrir arquivo:", e)
            sock.sendto(b"ERRO: Falha ao ler o arquivo.", addr)
    else:
        sock.sendto(b"ERRO: Indice invalido.", addr) # não pode enviar acento

def recieve_file(nome, addr, sock):
    try:
        with open(os.path.join(FILES_DIR, nome), 'wb') as f:
            while True:
                data, _ = sock.recvfrom(BUFFER_SIZE)
                if data == b"EOF":
                    break
                f.write(data)
        print(f"[+] Arquivo '{nome}' recebido de {addr}")
    except Exception as e:
        print("Erro ao receber arquivo:", e)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"[Servidor iniciado em {HOST}:{PORT}]")

while True:
    try:
        data, addr = sock.recvfrom(1024)
        msg = data.decode()

        if msg == "LISTAR":
            arquivos = list_files()
            sock.sendto(json.dumps(arquivos).encode(), addr)

        elif msg.startswith("DOWNLOAD"):
            _, index = msg.split()
            send_file(index, addr, sock)

        elif msg.startswith("UPLOAD"):
            _, senha, nome = msg.split(maxsplit=2)
            if senha == UPLOAD_PASSWORD:
                sock.sendto(b"OK", addr)
                recieve_file(nome, addr, sock)
            else:
                sock.sendto(b"ERRO: Senha incorreta.", addr)

        else:
            sock.sendto(b"ERRO: Comando invalido.", addr)

    except Exception as e:
        print("[ERRO GERAL]", e)