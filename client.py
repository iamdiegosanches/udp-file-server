import socket
import json

HOST = '200.239.153.138'
PORT = 2003

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    request_message = "Solicitação de arquivos"
    s.sendto(request_message.encode(), (HOST, PORT))

    data, addr = s.recvfrom(1024)
    file_names = json.loads(data.decode('utf-8'))
    print(f"Arquivos disponíveis: {file_names}")

    index_file = input("Index: ")
    s.sendto(index_file.encode(), (HOST, PORT))

    # Recebe o arquivo e salva localmente
    with open(f'baixado_{index_file}.txt', 'wb') as f:  # Nome do arquivo com o índice
        while True:
            data, addr = s.recvfrom(1024*5)
            print(f"data: {data}")
            if not data:
                break
            f.write(data)
    print("Arquivo recebido e salvo.")
