import socket
import json
import os

SERVER = 'ip'
PORT = 2003
BUFFER_SIZE = 1024 * 5

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def list():
    sock.sendto(b"LISTAR", (SERVER, PORT))
    data, _ = sock.recvfrom(65535)
    return json.loads(data.decode())

def download(index):
    sock.sendto(f"DOWNLOAD {index}".encode(), (SERVER, PORT))

    # Recebe nome real do arquivo primeiro
    name_file, _ = sock.recvfrom(1024)
    name = name_file.decode()

    if name.startswith("ERRO"):
        print(name)
        return

    with open(f"baixado_{name}", 'wb') as f:
        while True:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            if data == b"EOF":
                break
            f.write(data)
    print(f"[✔] Arquivo '{name}' salvo com sucesso.")

def send(caminho, senha):
    name = os.path.basename(caminho)
    sock.sendto(f"UPLOAD {senha} {name}".encode(), (SERVER, PORT))

    answer, _ = sock.recvfrom(1024)
    if answer != b"OK":
        print(answer.decode())
        return

    with open(caminho, 'rb') as f:
        while (chunk := f.read(BUFFER_SIZE)):
            sock.sendto(chunk, (SERVER, PORT))
    sock.sendto(b"EOF", (SERVER, PORT))
    print(f"[✔] Enviado '{name}' com sucesso.")

try:
    arquivos = list()
    print("Arquivos disponíveis:")
    for i, name in arquivos.items():
        print(f"{i}: {name}")

    option = input("Digite o índice para baixar ou 'u' para enviar arquivo: ")

    if option.lower() == 'u':
        path = input("Caminho do arquivo local: ")
        password = input("Senha de upload: ")
        if os.path.exists(path):
            send(path, password)
        else:
            print("Arquivo não encontrado.")
    else:
        download(option)

except Exception as e:
    print("[ERRO NO CLIENTE]", e)
finally:
    sock.close()
