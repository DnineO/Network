from socket import *


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
