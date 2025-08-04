import socket
import json
import os
import logging
import time

SERVER = 'ip'
PORT = 2003
BUFFER_SIZE = 1024 * 5

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def list():
    sock.sendto(b"LISTAR", (SERVER, PORT))
    data, _ = sock.recvfrom(65535)
    return json.loads(data.decode())

def download(index, pasta_destino="."):
    logging.basicConfig(level=logging.INFO)

    sock.sendto(f"DOWNLOAD {index}".encode(), (SERVER, PORT))

    name_file, _ = sock.recvfrom(1024)
    name = name_file.decode()

    if name.startswith("ERRO"):
        print(name)
        return None
    
    path_save = os.path.join(pasta_destino, f"baixado_{name}")
    with open(path_save, 'wb') as f:
        total = 0
        while True:
            try:
                data, _ = sock.recvfrom(BUFFER_SIZE)

                if data == b"EOF":
                    logging.info(f"FIM")
                    break

                f.write(data)
                total += len(data)
            except Exception as e:
                logging.basicConfig(level=logging.ERROR)
                logging.error(f"ERRO: {e}")

    logging.info(f"[✔] Arquivo '{name}' salvo com sucesso ({total} bytes).")

    if total == 0:
        return None

    return name

def send(caminho, senha):
    logging.basicConfig(level=logging.INFO)

    name = os.path.basename(caminho)
    sock.sendto(f"UPLOAD {senha} {name}".encode(), (SERVER, PORT))

    answer, _ = sock.recvfrom(1024)
    if answer != b"OK":
        logging.info(answer.decode())
        return

    with open(caminho, 'rb') as f:
        while (chunk := f.read(BUFFER_SIZE)):
            sock.sendto(chunk, (SERVER, PORT))
            time.sleep(0.2) # Atrasando um pouco o envio para que o servidor possa processar os dados

    sock.sendto(b"EOF", (SERVER, PORT))
    
    logging.info(f"[✔] Enviado '{name}' com sucesso.")

# try:
#     arquivos = list()
#     print("Arquivos disponíveis:")
#     for i, name in arquivos.items():
#         print(f"{i}: {name}")

#     option = input("Digite o índice para baixar ou 'u' para enviar arquivo: ")

#     if option.lower() == 'u':
#         path = input("Caminho do arquivo local: ")
#         password = input("Senha de upload: ")
#         if os.path.exists(path):
#             send(path, password)
#         else:
#             print("Arquivo não encontrado.")
#     else:
#         download(option)

# except Exception as e:
#     print("[ERRO NO CLIENTE]", e)
# finally:
#     sock.close()
