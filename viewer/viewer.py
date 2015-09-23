from common.app import SingleApp
from common.string_util import random_word
from evdev.device import InputDevice
from common.input import get_input_from_reader
from common.connection import UnixSocketListener, UnixSocketServer
import ConfigParser
import os
import time
import random
import sys
import curses
import argparse


infile_path = "/dev/input/by-path/platform-i8042-serio-0-event-kbd"
r_init = 2
c_init = 10
generated = []

def get_console_size():
    rows, columns = map(int, os.popen('stty size', 'r').read().split())
    return rows, columns


def get_random_row_col(strw):
    r, c = get_console_size()
    return random.randint(r_init+1, r), random.randint(r_init+1, c - strw)

def get_new_random_row_col(strw):
    r, c = get_random_row_col(strw)
    while r in generated:
        r, c = get_random_row_col(strw)
    generated.append(r)
    return r, c

def get_approval(app, init_message):
    r, c = get_console_size()

    allow_code = random_word() 
    reject_code = random_word()

    appexec_message = "Executable: %s" % app.executable
    appexechash_message = "Executable hash: %s" % app.exec_hash
    allow_message = "to allow enter %s" % allow_code
    reject_message = "to reject enter %s" % reject_code

    app_exec_row, app_exec_col = get_random_row_col(len(appexec_message))
    app_exec_hash_row, app_exec_hash_col = get_random_row_col(len(appexechash_message))
    allow_row, allow_col = get_random_row_col(len(allow_message))
    reject_row, reject_col = get_random_row_col(len(reject_message))
    del generated[:]
    
    while True:
        stdscr = curses.initscr()
        curses.start_color()

        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)
        
        stdscr.addstr(app_exec_row, app_exec_col, appexec_message, curses.color_pair(3))
        stdscr.addstr(app_exec_hash_row, app_exec_hash_col, appexechash_message, curses.color_pair(3))
        stdscr.addstr(allow_row, allow_col, allow_message, curses.color_pair(2))
        stdscr.addstr(reject_row, reject_col, reject_message, curses.color_pair(1))

        stdscr.addstr(r_init, c_init, init_message + " : ", curses.A_REVERSE)

        stdscr.refresh()
        reader = InputDevice(infile_path)
        reader.grab()
        read_string = get_input_from_reader(reader)
        reader.ungrab()
        curses.endwin()
        if read_string == allow_code:
            return True
        elif read_string == reject_code:
            return False


config = ConfigParser.RawConfigParser()
config.read('viewer.conf')

sock_path = config.get("connection", "ui_sock")

accessable_from = config.get("access", "exe")
accessable_hash = config.get("access", "sha1")

apps = []
apps.append(SingleApp(accessable_from, accessable_hash))


print("[viewer] waiting for connection")
server_listener = UnixSocketListener(sock_path, apps)
server = server_listener.next_client()
print("[viewer] someone connected successfully")

while True:
    command = server.read_line().split()

    if command[0] == "end":
        break
    elif command[0] == "view":
        app = SingleApp(command[1], command[2])
        if get_approval(app, ' '.join(command[3:])):
            server.write_line("1")
        else:
            server.write_line("0")