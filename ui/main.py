import os
import time
from common.connection import UnixSocketClient
from common.sudo import *
import ConfigParser
import sys
import argparse
from common.db import db, App, SavedInfo
from api.api_listener import APIListener
from api.api import API

config = ConfigParser.RawConfigParser()
config.read('main.conf')

getpass_sock_path = config.get("connection", "getpass_sock")
checkpass_sock_path = config.get("connection", "checkpass_sock")
confirm_sock_path = config.get("connection", "confirm_sock")
api_sock_path = config.get("connection", "api_sock")
viewer_sock_path = config.get("connection", "viewer_sock")


normal_user = config.get("user", "username")

getpass_exe = config.get("executables", "getpass_exe")
checkpass_exe = config.get("executables", "checkpass_exe")
viewer_exe = config.get("executables", "viewer_exe")

def run_viewer(app, message):
    print("[main.py] running viewer to approve")
    run_command(get_command_openvt(sudo_user(normal_user, "./" + viewer_exe)))
    time.sleep(2)
    print("[main.py] going to connect to sock")
    viewer = UnixSocketClient(viewer_sock_path)
    viewer.write_line("view %s %s %s" % (app.executable, app.exec_hash, message ))
    read = viewer.read_line()
    viewer.write_line("end")
    if read is "1":
        return True
    return False


def approver(app):
    exec_eq = App.select().where(App.executable == app.executable)
    both_eq = exec_eq.where(App.exec_hash == app.exec_hash)

    if both_eq.exists():
        return True
    if exec_eq.exists(): #app update
        if run_viewer(app, "app's hash changed and now wants to update?"):
            API().update_app(app)
            return True
    else: #new app wants to connect
        if run_viewer(app, "new apps wants to connect allow or reject?"):
            API().register_app(app)
            return True
    return False


def init_loop():
    run_command(get_command_openvt(sudo_user(normal_user, "./" + getpass_exe)))
    run_command("./" + checkpass_exe)

    time.sleep(2)

    getpass_sock = UnixSocketClient(getpass_sock_path)
    checkpass_sock = UnixSocketClient(checkpass_sock_path)

    success = False
    master_password = ""

    while True:
        getpass_read = getpass_sock.read_line()

        if getpass_read[0] in ['0', '1']:
            checkpass_sock.write_line("end")

            if getpass_read[0] is '1':
                success = True
                master_password = getpass_read.split()[1]
            break

        checkpass_sock.write_line(getpass_read)
        getpass_sock.write_line(checkpass_sock.read_line())

    return success, master_password

parser = argparse.ArgumentParser()
parser.add_argument("--initdb", help="initialize db", action="store_true")
args = parser.parse_args()

if args.initdb:
    db.create_tables([App, SavedInfo])
    sys.exit(0)
success, master_password = init_loop()

if not success:
    print("initialization not successfull .exiting...")
    sys.exit(1)

db.connect()

api = APIListener(api_sock_path, master_password, approver)
api.run()
