from evdev.device import InputDevice
from common.connection import UnixSocketServer, UnixSocketListener
from common.connection import UnixSocketClient
from common.app import SingleApp
from common.input import get_input_from_reader
from common.sudo import *
from common.string_util import *
import random
import sys
import os
import time
import ConfigParser


config = ConfigParser.RawConfigParser()
config.read('passget.conf')

infile_path = config.get("input", "keyboard_dev")

ui_socket_path = config.get("connection", "ui_sock")

accessable_from = config.get("access", "exe")
accessable_hash = config.get("access", "sha1")


apps = []
apps.append(SingleApp(accessable_from, accessable_hash))


def ask_master_password(checkpass_socket):

    reader = InputDevice(infile_path)

    input_correct = False
    reader.grab()

    read_string = ""

    while True:
        os.system("clear")

        exit_code = random_word()
        checkpass_socket.write_line("secret_code")
        secret_code = checkpass_socket.read_line()
        print('your secret code is "%s"' % secret_code)
        print("please enter %s to exit or master password to continue : "
              % exit_code),
        sys.stdout.flush()
        read_string = get_input_from_reader(reader)
        if read_string == exit_code:
            break
        checkpass_socket.write_line("check " + read_string)
        result = checkpass_socket.read_line()
        if result == "1":
            input_correct = True
            break
    reader.ungrab() 
    return input_correct, read_string


def mainService():
    print("[getpass] waiting for ui to connect... ")
    ui_socket_listener = UnixSocketListener(
        ui_socket_path, apps)

    ui_socket = ui_socket_listener.next_client()
    print("[getpass] ui connected ... ")
    print("[getpass] asking master password... ")
    # os.setregid(os.getegid(), os.getegid())
    correct, master_password = ask_master_password(ui_socket)
    # os.setregid(os.getegid(), os.getegid())
    if correct:
        ui_socket.write_line("1 " + master_password)
    else:
        ui_socket.write_line("0")


mainService()