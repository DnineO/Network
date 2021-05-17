# -*- coding: utf-8 -*-
# CLIENT

from socket import *
import sys
import stun


def sigserver_exch():
    # КЛИЕНТ <-> СИГНАЛЬНЫЙ СЕРВЕР
    # КЛИЕНТ -> СЕРВЕР

    # КЛИЕНТ - отправляет запрос на СИГНАЛЬНЫЙ СЕРВЕР с белым IP
    # для получения текущих значений IP и PORT СЕРВЕРА за NAT для подключения к нему.

    # Внешний IP и PORT СИГНАЛЬНОГО СЕРВЕРА:
    v_sig_host = 'XX.XX.XX.XX'
    v_sig_port = XXXX

    # id этого КЛИЕНТА, имя этого КЛИЕНТА, id искомого СЕРВЕРА
    v_id_client = 'id_client_1001'
    v_name_client = 'name_client_1'
    v_id_server = 'id_server_1002'

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
        # и id_dest - id известного сервера с которым хотим связаться.
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

        # Отправим сообщение на СИГНАЛЬНЫЙ СЕРВЕР
        udp_socket.sendto(data_out, addr_sigserv)

        while True:
        # Если первый элемент списка - 'sigserv' (сообщение от СИГНАЛЬНОГО СЕРВЕРА),
        # печатаем сообщение с полученными данными и отправляем сообщение
        # 'Hello, SERVER!' на сервер по указанному в сообщении адресу.
        data_in = udp_socket.recvfrom(1024)
        data_0 = data_in[0]
        data_p = data_0.split(",")
        if data_p[0] == 'sigserv':
            print('signal server data: ', data_p)
            udp_socket.sendto('Hello, SERVER!', (data_p[3], int(data_p[4])))
        else:
            print("No, it is not Rio de Janeiro!")
        udp_socket.close()

    except:
        print('Exit!')
        sys.exit(1)

    finally:
        if udp_socket <> ''
            udp_socket.close()


sigserver_exch()