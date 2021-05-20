#!/usr/bin/env python
# -*- coding: utf-8 -*-

from socket import *
import sys

# sock = socket.socket()
#
# sock.connect(('localhost', 9080))
#
# sock.send('hello'.encode())
#
# data = sock.recv(1024)
# sock.close()
#
# print(data)

host = 'localhost'
port = 9080
addr = (host, port)

udp_socket = socket(AF_INET, SOCK_DGRAM)

data = input('write to server: ')
if not data:
    udp_socket.close()
    sys.exit(1)

data = data.encode()
udp_socket.sendto(data, addr)
data = bytes.decode(data)
data = udp_socket.recvfrom(1024)
print(data)

udp_socket.close()
