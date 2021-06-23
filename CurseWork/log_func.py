import time
import os

LOG_FILE_NAME = "log_file.txt"
LOG_FILE = None


def open_file():
    global LOG_FILE
    if os.path.exists(LOG_FILE_NAME):
        LOG_FILE = open(LOG_FILE_NAME, 'a')
    else:
        LOG_FILE = open(LOG_FILE_NAME, 'w')


def close_file():
    global LOG_FILE
    LOG_FILE.close()


def log(func, cmd):
    global LOG_FILE
    logmsg = time.strftime("%Y-%m-%d %H-%M-%S [-] " + func)
    print("\033[31m%s\033[0m: \033[32m%s\033[0m" % (logmsg, cmd))

    try:
        open_file()
        LOG_FILE.write("[%s]: %s" % (logmsg, cmd) + "\r")
    except Exception as err:
        print(err)
    close_file()
