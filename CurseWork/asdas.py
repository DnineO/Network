import sys
import traceback
import math
import random
import socket
import threading
from tkinter import *
from tkinter.filedialog import asksaveasfilename
import logging
import time
import os

isCLI = False  # true коммандная строка TODO:коммандную строку, не все возможности

conn_array = []  # список сокетов
secret_array = dict()
username_array = dict()
contact_array = dict()

username = "User"

location = 0
port = 0
top = ""

LOG_FILE_NAME = "log_file.txt"
LOG_FILE = None

main_body_text = 0


def binWord(word):
    master = ""
    for letter in word:
        temp = bin(ord(letter))[2:]
        while len(temp) < 7:
            temp = '0' + temp
        master = master + temp
    return master


def xcrypt(message, key):
    count = 0
    master = ""
    for letter in message:
        if count == len(key):
            count = 0
        master += str(int(letter) ^ int(key[count]))
        count += 1
    return master


def x_encode(string, number):
    return xcrypt(binWord(string), bin(number)[2:])


def refract(binary):
    master = ""
    for x in range(0, int(len(binary) / 7)):
        master += chr(int(binary[x * 7: (x + 1) * 7], 2) + 0)
    return master


def formatNumber(number):
    temp = str(number)
    while len(temp) < 4:
        temp = '0' + temp
    return temp


def netThrow(conn, secret, message):
    try:
        conn.send(formatNumber(len(x_encode(message, secret))).encode())
        conn.send(x_encode(message, secret).encode())
    except socket.error:
        if len(conn_array) != 0:
            log("System", "Connection issue. Sending message failed.")
            writeToScreen("Connection issue. Sending message failed.", "System")
            processFlag("-001")


def netCatch(conn, secret):
    try:
        data = conn.recv(4)
        if data.decode()[0] == '-':
            processFlag(data.decode(), conn)
            return 1
        data = conn.recv(int(data.decode()))
        return refract(xcrypt(data.decode(), bin(secret)[2:]))
    except socket.error:
        if len(conn_array) != 0:
            log("System", "Connection issue. Receiving message failed.")
            writeToScreen("Connection issue. Receiving message failed.", "System")
        processFlag("-001")


def isPrime(number):
    x = 1
    if number == 2 or number == 3:
        return True
    while x < math.sqrt(number):
        x += 1
        if number % x == 0:
            return False
    return True


def processFlag(number, conn=None):
    global statusConnect
    global conn_array
    global secret_array
    global username_array
    global contact_array
    global isCLI
    t = int(number[1:])
    if t == 1:
        if len(conn_array) == 1:
            log("System", "Connection closed.")
            writeToScreen("Connection closed.", "System")
            dump = secret_array.pop(conn_array[0])
            dump = conn_array.pop()
            try:
                dump.close()
            except socket.error:
                log("System", "Issue with someone being bad about disconnecting")
                print("Issue with someone being bad about disconnecting")
            if not isCLI:
                statusConnect.set("Connect")
                connecter.config(state=NORMAL)
            return

        if conn != None:
            log("System", "Connect to " + conn.getsockname()[0] + " closed.")
            writeToScreen("Connect to " + conn.getsockname()[0] + " closed.", "System")
            dump = secret_array.pop(conn)
            conn_array.remove(conn)
            conn.close()

    if t == 2:
        name = netCatch(conn, secret_array[conn])
        if (isUsernameFree(name)):
            log("System", "User " + username_array[conn] + " has changed their username to " + name)
            writeToScreen(
                "User " + username_array[conn] + " has changed their username to " + name, "System")
            username_array[conn] = name
            contact_array[
                conn.getpeername()[0]] = [conn.getpeername()[1], name]
    if t == 4:
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        Client(data.decode(),
               int(contact_array[conn.getpeername()[0]][0])).start()


def processUserCommands(command, param):
    global conn_array
    global secret_array
    global username

    if command == "nick":
        for letter in param[0]:
            if letter == " " or letter == "\n":
                if isCLI:
                    log("System", "Invalid username. No spaces allowed.")
                    error_window(0, "Invalid username. No spaces allowed.")
                else:
                    log("System", "Invalid username. No spaces allowed.")
                    error_window(root, "Invalid username. No spaces allowed.")
                return
        if isUsernameFree(param[0]):
            log("System", "Username is being changed to " + param[0])
            writeToScreen("Username is being changed to " + param[0], "System")
            for conn in conn_array:
                conn.send("-002".encode())
                netThrow(conn, secret_array[conn], param[0])
            username = param[0]
        else:
            log("System", param[0] + " is already taken as a username")
            writeToScreen(param[0] +
                          " is already taken as a username", "System")
    if command == "disconnect":
        for conn in conn_array:
            conn.send("-001".encode())
        processFlag("-001")
    if command == "connect":
        if (options_sanitation(param[1], param[0])):
            Client(param[0], int(param[1])).start()
    if command == "host":
        if (options_sanitation(param[0])):
            Server(int(param[0])).start()


def isUsernameFree(name):
    global username_array
    global username
    for conn in username_array:
        if name == username_array[conn] or name == username:
            return False
    return True


def passFriends(conn):
    global conn_array
    for connection in conn_array:
        if conn != connection:
            conn.send("-004".encode())
            conn.send(
                formatNumber(len(connection.getpeername()[0])).encode())
            conn.send(connection.getpeername()[0].encode())


def client_options_window(master):
    top = Toplevel(master)
    top.title("Connection options")
    top.protocol("WM_DELETE_WINDOW", lambda: optionDelete(top))
    top.grab_set()
    Label(top, text="Server IP:").grid(row=0)
    location = Entry(top)
    location.grid(row=0, column=1)
    location.focus_set()
    Label(top, text="Port:").grid(row=1)
    port = Entry(top)
    port.grid(row=1, column=1)
    go = Button(top, text="Connect", command=lambda:
    client_options_go(location.get(), port.get(), top))
    go.grid(row=2, column=1)


def client_options_go(dest, port, window):
    if options_sanitation(port, dest):
        if not isCLI:
            window.destroy()
        Client(dest, int(port)).start()
    elif isCLI:
        sys.exit(1)


def options_sanitation(por, loc=""):
    global root
    if isCLI:
        root = 0
    if not por.isdigit():
        log("System", "Please input a port number.")
        error_window(root, "Please input a port number.")
        return False
    if int(por) < 0 or 65555 < int(por):
        log("System", "Please input a port number between 0 and 65555")
        error_window(root, "Please input a port number between 0 and 65555")
        return False
    if loc != "":
        if not ip_process(loc.split(".")):
            log("System", "Please input a valid ip address.")
            error_window(root, "Please input a valid ip address.")
            return False
    return True


def ip_process(ipArray):
    if len(ipArray) != 4:
        return False
    for ip in ipArray:
        if not ip.isdigit():
            return False
        t = int(ip)
        if t < 0 or 255 < t:
            return False
    return True


def server_options_window(master):
    top = Toplevel(master)
    top.title("Connection options")
    top.grab_set()
    top.protocol("WM_DELETE_WINDOW", lambda: optionDelete(top))
    Label(top, text="Port:").grid(row=0)
    port = Entry(top)
    port.grid(row=0, column=1)
    port.focus_set()
    go = Button(top, text="Launch", command=lambda:
    server_options_go(port.get(), top))
    go.grid(row=1, column=1)


def server_options_go(port, window):
    if options_sanitation(port):
        if not isCLI:
            window.destroy()
        Server(int(port)).start()
    elif isCLI:
        sys.exit(1)


def username_options_window(master):
    top = Toplevel(master)
    top.title("Username options")
    top.grab_set()
    Label(top, text="Username:").grid(row=0)
    name = Entry(top)
    name.focus_set()
    name.grid(row=0, column=1)
    go = Button(top, text="Change", command=lambda:
    username_options_go(name.get(), top))
    go.grid(row=1, column=1)


def username_options_go(name, window):
    processUserCommands("nick", [name])
    window.destroy()


def error_window(master, texty):
    global isCLI
    if isCLI:
        log("System", texty)
        writeToScreen(texty, "System")
    else:
        window = Toplevel(master)
        window.title("ERROR")
        window.grab_set()
        Label(window, text=texty).pack()
        go = Button(window, text="OK", command=window.destroy)
        go.pack()
        go.focus_set()


def optionDelete(window):
    connecter.config(state=NORMAL)
    window.destroy()


def contacts_window(master):
    global contact_array
    cWindow = Toplevel(master)
    cWindow.title("Contacts")
    cWindow.grab_set()
    scrollbar = Scrollbar(cWindow, orient=VERTICAL)
    listbox = Listbox(cWindow, yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    buttons = Frame(cWindow)
    cBut = Button(buttons, text="Connect",
                  command=lambda: contacts_connect(
                      listbox.get(ACTIVE).split(" ")))
    cBut.pack(side=LEFT)
    dBut = Button(buttons, text="Remove",
                  command=lambda: contacts_remove(
                      listbox.get(ACTIVE).split(" "), listbox))
    dBut.pack(side=LEFT)
    aBut = Button(buttons, text="Add",
                  command=lambda: contacts_add(listbox, cWindow))
    aBut.pack(side=LEFT)
    buttons.pack(side=BOTTOM)

    for person in contact_array:
        listbox.insert(END, contact_array[person][1] + " " +
                       person + " " + contact_array[person][0])
    listbox.pack(side=LEFT, fill=BOTH, expand=1)


def contacts_connect(item):
    Client(item[1], int(item[2])).start()


def contacts_remove(item, listbox):
    if listbox.size() != 0:
        listbox.delete(ACTIVE)
        global contact_array
        h = contact_array.pop(item[1])


def contacts_add(listbox, master):
    aWindow = Toplevel(master)
    aWindow.title("Contact add")
    Label(aWindow, text="Username:").grid(row=0)
    name = Entry(aWindow)
    name.focus_set()
    name.grid(row=0, column=1)
    Label(aWindow, text="IP:").grid(row=1)
    ip = Entry(aWindow)
    ip.grid(row=1, column=1)
    Label(aWindow, text="Port:").grid(row=2)
    port = Entry(aWindow)
    port.grid(row=2, column=1)
    go = Button(aWindow, text="Add", command=lambda:
    contacts_add_helper(name.get(), ip.get(), port.get(),
                        aWindow, listbox))
    go.grid(row=3, column=1)


def contacts_add_helper(username, ip, port, window, listbox):
    for letter in username:
        if letter == " " or letter == "\n":
            log("System", "Invalid username. No spaces allowed.")
            error_window(root, "Invalid username. No spaces allowed.")
            return
    if options_sanitation(port, ip):
        listbox.insert(END, username + " " + ip + " " + port)
        contact_array[ip] = [port, username]
        window.destroy()
        return


def load_contacts():
    global contact_array
    try:
        filehandle = open("data\\contacts.dat", "r")
    except IOError:
        return
    line = filehandle.readline()
    while len(line) != 0:
        temp = (line.rstrip('\n')).split(" ")  # format: ip, port, name
        contact_array[temp[0]] = temp[1:]
        line = filehandle.readline()
    filehandle.close()


def dump_contacts():
    global contact_array
    try:
        filehandle = open("data\\contacts.dat", "w")
    except IOError:
        log("System", "Can't dump contacts.")
        print("Can't dump contacts.")
        return
    for contact in contact_array:
        filehandle.write(
            contact + " " + str(contact_array[contact][0]) + " " +
            contact_array[contact][1] + "\n")
    filehandle.close()


def placeText(text):
    global conn_array
    global secret_array
    global username

    log(username, text)
    writeToScreen(text, username)
    for person in conn_array:
        netThrow(person, secret_array[person], text)


def writeToScreen(text, username=""):
    global main_body_text
    global isCLI
    if isCLI:
        if username:
            print(username + ": " + text)
        else:
            print(text)
    else:
        main_body_text.config(state=NORMAL)
        main_body_text.insert(END, '\n')
        if username:
            main_body_text.insert(END, username + ": ")
        main_body_text.insert(END, text)
        main_body_text.yview(END)
        main_body_text.config(state=DISABLED)


def processUserText(event):
    data = text_input.get()
    if data[0] != "/":
        placeText(data)
    else:
        if data.find(" ") == -1:
            command = data[1:]
        else:
            command = data[1:data.find(" ")]
        params = data[data.find(" ") + 1:].split(" ")
        processUserCommands(command, params)
    text_input.delete(0, END)


def processUserInput(text):  # for CLI
    if text[0] != "/":
        placeText(text)
    else:
        if text.find(" ") == -1:
            command = text[1:]
        else:
            command = text[1:text.find(" ")]
        params = text[text.find(" ") + 1:].split(" ")
        processUserCommands(command, params)


def openFile():
    global LOG_FILE
    if os.path.exists(LOG_FILE_NAME):
        LOG_FILE = open(LOG_FILE_NAME, 'a')
    else:
        LOG_FILE = open(LOG_FILE_NAME, 'w')


def closeFile():
    global LOG_FILE
    LOG_FILE.close()


def log(func, cmd):
    global LOG_FILE
    logmsg = time.strftime("%Y-%m-%d %H-%M-%S [-] " + func)
    print("\033[31m%s\033[0m: \033[32m%s\033[0m" % (logmsg, cmd))

    try:
        openFile()
        LOG_FILE.write("[%s]: %s" % (logmsg, cmd) + "\r")
    except Exception as err:
        print(err)
    closeFile()


class Server(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        global conn_array
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        if len(conn_array) == 0:
            log("System", "Socket is good, waiting for connections on port:" + str(self.port))
            writeToScreen(
                "Socket is good, waiting for connections on port: " +
                str(self.port), "System")
        s.listen(1)
        global conn_init
        conn_init, addr_init = s.accept()
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.bind(('', 0))
        serv.listen(1)

        portVal = str(serv.getsockname()[1])
        if len(portVal) == 5:
            conn_init.send(portVal.encode())
        else:
            conn_init.send(("0" + portVal).encode())

        conn_init.close()
        conn, addr = serv.accept()
        conn_array.append(conn)
        log("System", "Connected by " + str(addr[0]))
        writeToScreen("Connected by " + str(addr[0]), "System")

        global statusConnect
        statusConnect.set("Disconnect")
        connecter.config(state=NORMAL)

        prime = random.randint(1000, 9000)
        while not isPrime(prime):
            prime = random.randint(1000, 9000)
        base = random.randint(20, 100)
        a = random.randint(20, 100)

        conn.send(formatNumber(len(str(base))).encode())
        conn.send(str(base).encode())

        conn.send(formatNumber(len(str(prime))).encode())
        conn.send(str(prime).encode())

        conn.send(formatNumber(len(str(pow(base, a) % prime))).encode())
        conn.send(str(pow(base, a) % prime).encode())

        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        b = int(data.decode())

        global secret_array
        secret = pow(b, a) % prime
        secret_array[conn] = secret

        conn.send(formatNumber(len(username)).encode())
        conn.send(username.encode())

        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        if data.decode() != "Self":
            username_array[conn] = data.decode()
            contact_array[str(addr[0])] = [str(self.port), data.decode()]
        else:
            username_array[conn] = addr[0]
            contact_array[str(addr[0])] = [str(self.port), "No_nick"]

        passFriends(conn)
        threading.Thread(target=Runner, args=(conn, secret)).start()
        Server(self.port).start()


class Client(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.port = port
        self.host = host

    def run(self):
        global conn_array
        global secret_array
        conn_init = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_init.settimeout(5.0)
        try:
            conn_init.connect((self.host, self.port))
        except socket.timeout:
            log("System", "Timeout issue. Host possible not there.")
            writeToScreen("Timeout issue. Host possible not there.", "System")
            connecter.config(state=NORMAL)
            raise SystemExit(0)
        except socket.error:
            log("System", "Connection issue. Host actively refused connection.")
            writeToScreen(
                "Connection issue. Host actively refused connection.", "System")
            connecter.config(state=NORMAL)
            raise SystemExit(0)
        porta = conn_init.recv(5)
        porte = int(porta.decode())
        conn_init.close()
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.host, porte))

        log("System", "Connected to: " + self.host + " on port: " + str(porte))
        writeToScreen("Connected to: " + self.host + " on port: " + str(porte), "System")

        global statusConnect
        statusConnect.set("Disconnect")
        connecter.config(state=NORMAL)

        conn_array.append(conn)
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        base = int(data.decode())
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        prime = int(data.decode())
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        a = int(data.decode())
        b = random.randint(20, 100)
        conn.send(formatNumber(len(str(pow(base, b) % prime))).encode())
        conn.send(str(pow(base, b) % prime).encode())
        secret = pow(a, b) % prime
        secret_array[conn] = secret

        conn.send(formatNumber(len(username)).encode())
        conn.send(username.encode())

        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        if data.decode() != "Self":
            username_array[conn] = data.decode()
            contact_array[
                conn.getpeername()[0]] = [str(self.port), data.decode()]
        else:
            username_array[conn] = self.host
            contact_array[conn.getpeername()[0]] = [str(self.port), "No_nick"]
        threading.Thread(target=Runner, args=(conn, secret)).start()


def Runner(conn, secret):
    global username_array
    while 1:
        data = netCatch(conn, secret)
        if data != 1:
            log(username_array[conn], data)
            writeToScreen(data, username_array[conn])


def QuickClient():
    window = Toplevel(root)
    window.title("Connection options")
    window.grab_set()
    Label(window, text="Server IP:").grid(row=0)
    destination = Entry(window)
    destination.grid(row=0, column=1)
    go = Button(window, text="Connect", command=lambda:
    client_options_go(destination.get(), "9999", window))
    go.grid(row=1, column=1)


def QuickServer():
    Server(9999).start()


def saveHistory():
    global main_body_text
    file_name = asksaveasfilename(
        title="Choose save location",
        filetypes=[('Plain text', '*.txt'), ('Any File', '*.*')])
    try:
        filehandle = open(file_name + ".txt", "w")
    except IOError:
        log("System", "Can't save history.")
        error_window(root, "Can't save history.")
        print("Can't save history.")
        return
    contents = main_body_text.get(1.0, END)
    for line in contents:
        filehandle.write(line)
    filehandle.close()
    log("System", "History saved.")
    print("History saved.")


def connects(clientType):
    global conn_array
    connecter.config(state=DISABLED)
    if len(conn_array) == 0:
        if clientType == 0:
            client_options_window(root)
        if clientType == 1:
            server_options_window(root)
    else:
        for connection in conn_array:
            connection.send("-001".encode())
        processFlag("-001")


def toOne():
    global clientType
    clientType = 0


def toTwo():
    global clientType
    clientType = 1


if len(sys.argv) > 1 and sys.argv[1] == "-cli":
    log("System", "Starting command line chat")
    print("Starting command line chat")

else:
    root = Tk()
    root.title("Chat")

    menubar = Menu(root)

    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label="Save chat", command=lambda: saveHistory())
    file_menu.add_command(label="Change username",
                          command=lambda: username_options_window(root))
    file_menu.add_command(label="Exit", command=lambda: root.destroy())
    menubar.add_cascade(label="File", menu=file_menu)

    connection_menu = Menu(menubar, tearoff=0)
    connection_menu.add_command(label="Quick Connect", command=QuickClient)
    connection_menu.add_command(
        label="Connect on port", command=lambda: client_options_window(root))
    connection_menu.add_command(
        label="Disconnect", command=lambda: processFlag("-001"))
    menubar.add_cascade(label="Connect", menu=connection_menu)

    server_menu = Menu(menubar, tearoff=0)
    server_menu.add_command(label="Launch server", command=QuickServer)
    server_menu.add_command(label="Listen on port",
                            command=lambda: server_options_window(root))
    menubar.add_cascade(label="Server", menu=server_menu)

    menubar.add_command(label="Contacts", command=lambda:
    contacts_window(root))

    root.config(menu=menubar)

    main_body = Frame(root, height=20, width=50)

    main_body_text = Text(main_body)
    body_text_scroll = Scrollbar(main_body)
    main_body_text.focus_set()
    body_text_scroll.pack(side=RIGHT, fill=Y)
    main_body_text.pack(side=LEFT, fill=Y)
    body_text_scroll.config(command=main_body_text.yview)
    main_body_text.config(yscrollcommand=body_text_scroll.set)
    main_body.pack()
    log("System", "Welcome to the chat program!")
    main_body_text.insert(END, "Welcome to the chat program!")
    main_body_text.config(state=DISABLED)

    text_input = Entry(root, width=60)
    text_input.bind("<Return>", processUserText)
    text_input.pack()

    statusConnect = StringVar()
    statusConnect.set("Connect")
    clientType = 1
    Radiobutton(root, text="Client", variable=clientType,
                value=0, command=toOne).pack(anchor=E)
    Radiobutton(root, text="Server", variable=clientType,
                value=1, command=toTwo).pack(anchor=E)
    connecter = Button(root, textvariable=statusConnect,
                       command=lambda: connects(clientType))
    connecter.pack()

    load_contacts()

    # ------------------------------------------------------------

    root.mainloop()

    # dump_contacts()
