import socket
import threading
import os
import json

HOST = '200.239.153.138'  # Localhost
PORT = 2003        # Port to listen on

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    s.bind((HOST, PORT))
except socket.error as e:
    print("Erro: ", e)

print("Server waiting connections...")

idCount = 0

def threaded_client(conn, user):
    global idCount

    while True:
        try:
            pass
        except:
            pass

def read_names_files(path):
    try:
        file_names = os.listdir(path)
        file_names = dict(enumerate(file_names))
        return file_names
    except FileNotFoundError:
        print(f"Error: Folder {path} not found")
        return {}

def send_file(index, addr, buffer_size=1024*5):
    file_names = read_names_files('files')
    file = file_names.get(int(index))
    if file:
        with open(f'files/{file}', 'rb') as f:
            while True:
                data = f.read(buffer_size)
                if not data:
                    break
                s.sendto(data, addr)
    else:
        print("Índice de arquivo inválido.")


while True:
    data, addr = s.recvfrom(1024)
    data_decoded = data.decode('utf-8')
    if data_decoded.startswith("Index: "):
        index = data_decoded.split()[-1]
        send_file(index, addr)
    elif data_decoded.startswith("Solicitação de arquivos"):
        print(f"Recebido de {addr}")

        file_names = read_names_files('files')

        response = json.dumps(file_names).encode('utf-8')
        s.sendto(response, addr)
