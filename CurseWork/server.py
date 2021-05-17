# -*- coding: utf-8 -*-
# SERVER

from socket import *
import sys
import stun


def sigserver_exch():
    # СЕРВЕР <-> СИГНАЛЬНЫЙ СЕРВЕР
    # СЕРВЕР <- КЛИЕНТ

    # СЕРВЕР - отправляет запрос на СИГНАЛЬНЫЙ СЕРВЕР с белым статическим IP со своими данными о текущих значениях IP и PORT. Принимает запрос от КЛИЕНТА.

    # Внешний IP и PORT СИГНАЛЬНОГО СЕРВЕРА:
    v_sig_host = 'XX.XX.XX.XX'
    v_sig_port = XXXX

    # id этого КЛИЕНТА, имя этого КЛИЕНТА, id искомого СЕРВЕРА
    v_id_client = 'id_server_1002'
    v_name_client = 'name_server_2'
    v_id_server = 'none'

    # IP и PORT этого КЛИЕНТА
    v_ip_localhost = 'XX.XX.XX.XX'
    v_port_localhost = XXXX


udp_socket = ''
try:
    # Получаем текущий внешний IP и PORT при помощи утилиты STUN
    nat_type, external_ip, external_port = stun.get_ip_info()

    # Присваиваем переменным белый IP и PORT сигнального сервера для отправки запроса
    host_sigserver = v_sig_host
    port_sigserver = v_sig_port
    addr_sigserv = (host_sigserver, port_sigserver)

    # Заполняем словарь данными для отправки на СИГНАЛЬНЫЙ СЕРВЕР:
    # текущий id + имя + текущий внешний IP и PORT,
    # и id_dest - укажем 'none'
    # В качестве id можно использовать хеш случайного числа + соль
    data_out = v_id_client + ',' + v_name_client + ',' + external_ip + ',' + str(external_port) + ',' + v_id_server

    # Создадим сокет с атрибутами:
    # использовать пространство интернет адресов (AF_INET),
    # передавать данные в виде отдельных сообщений
    udp_socket = socket(AF_INET, SOCK_DGRAM)

    # Присвоим переменным свой локальный IP и свободный PORT для получения информации
    host = v_ip_localhost
    port = v_port_localhost
    addr = (host, port)

    # Свяжем сокет с локальными IP и PORT
    udp_socket.bind(addr)
    print('socket binding')

    # Отправим сообщение на СИГНАЛЬНЫЙ СЕРВЕР
    udp_socket.sendto(data_out, addr_sigserv)

    while True:
        # Если первый элемент списка - 'sigserv' (сообщение от СИГНАЛЬНОГО СЕРВЕРА),
        # печатаем сообщение с полученными данными
        # Иначе - печатаем сообщение 'Message from CLIENT!'
        data_in = udp_socket.recvfrom(1024)
        if data_in[0] == 'sigserv':
            print('signal server data: ', data_in)
        else:
            print('Message from CLIENT!')

    # Закрываем сокет
    udp_socket.close()

except:
    print('exit!')
    sys.exit(1)

finally:
    if udp_socket <> ''
        udp_socket.close()

sigserver_exch()