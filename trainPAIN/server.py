from socket import *

# sock = socket.socket()
#
# port = 9080
# ip = ''
#
# # связка сокета с хостом и портом
# sock.bind((ip, port))
#
# # слушаем, с очередью 1
# sock.listen(1)
#
# # принятие подключения, кортеж: новый сокет, адрес клиента
# conn, addr = sock.accept()
#
# print('connected', addr)
#
# while True:
#     data = conn.recv(1024)
#     if not data:
#         break
#     conn.send(data.upper())
#     print('get', data)
# conn.close()


host = 'localhost'
port = 9080
addr = (host, port)

udp_socket = socket(AF_INET, SOCK_DGRAM)
udp_socket.bind(addr)

while True:
    question = input('Exit? y/n: ')
    if question == "y":
        break

    print('waiting...')

    data, addr = udp_socket.recvfrom(1024)
    print('client: ', addr, ' // mess: ', data)

    udp_socket.sendto(b'message received by the server ', addr)

udp_socket.close()
