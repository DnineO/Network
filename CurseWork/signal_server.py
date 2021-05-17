# -*- coding: utf-8 -*-
# SIGNAL SERVER

# Twisted - управляемая событиями(event) структура
# Событиями управляют функции – event handler
# Цикл обработки событий отслеживает события и запускает соответствующие event handler
# Работа цикла лежит на объекте reactor из модуля twisted.internet

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
import sys, os
import sqlite3


class Query_processing_server(DatagramProtocol):
    # СИГНАЛЬНЫЙ СЕРВЕР <-> КЛИЕНТ
    # КЛИЕНТ -> СЕРВЕР
    # либо
    # СИГНАЛЬНЫЙ СЕРВЕР <-> СЕРВЕР

    # СИГНАЛЬНЫЙ СЕРВЕР - принимает запросы от КЛИЕНТА и СЕРВЕРА
    # сохраняет их текущие значения IP и PORT
    # (если отсутствуют - создает новые + имя и идентификатор)
    # и выдает IP и PORT СЕРВЕРА запрошенного КЛИЕНТОМ.

    def datagramReceived(self, data, addr_out):
        conn = ''
        try:
            # Разбиваем полученные данные по разделителю (,) [id_host,name_host,external_ip,external_port,id_dest]
            # id_dest - искомый id сервера
            data = data.split(",")

            # Запрос на указание пути к файлу БД sqlite3, при отсутствии будет создана новая БД по указанному пути:
            path_to_db = raw_input('Enter name db. For example: "/home/user/new_db.db": ')
            path_to_db = os.path.join(path_to_db)
            # Создать соединение с БД
            conn = sqlite3.connect(path_to_db)
            # Преобразовывать байтстроку в юникод
            conn.text_factory = str
            # Создаем объект курсора
            c = conn.cursor()
            # Создаем таблицу соответствия для хостов
            c.execute('''CREATE TABLE IF NOT EXISTS compliance_table ("id_host" text UNIQUE, "name_host" text, "ip_host" text, \
            	"port_host" text)''')

            # Добавляем новый хост, если еще не создан
            # Обновляем данные ip, port для существующего хоста
            c.execute('INSERT OR IGNORE INTO compliance_table VALUES (?, ?, ?, ?);', data[0:len(data) - 1])
            # Сохраняем изменения
            conn.commit()
            c.execute('SELECT * FROM compliance_table')

            # Поиск данных о сервере по его id
            c.execute('''SELECT id_host, name_host, ip_host, port_host from compliance_table WHERE id_host=?''',
                      (data[len(data) - 1],))
            cf = c.fetchone()
            if cf == None:
                print('Server_id not found!')
            else:
                # transport.write - отправка сообщения с данными: id_host, name_host, ip_host, port_host и меткой sigserver
                lst = 'sigserv' + ',' + cf[0] + ',' + cf[1] + ',' + cf[2] + ',' + cf[3]
                self.transport.write(str(lst), addr_out)
            # Закрываем соединение
            conn.close()
        except:
            print('Exit!')
            sys.exit(1)
        finally:
            if conn <> ''
                conn.close()


reactor.listenUDP(9102, Query_processing_server())
print('reactor run!')
reactor.run()