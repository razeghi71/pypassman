from common.connection import UnixSocketListener, UnixSocketServer
from common.app import SingleApp
import ConfigParser
import os
import time
from Crypto.Hash import SHA512

config = ConfigParser.RawConfigParser()
config.read('passcheck.conf')

sock_path = config.get("connection", "ui_sock")

accessable_from = config.get("access", "exe")
accessable_hash = config.get("access", "sha1")

apps = []
apps.append(SingleApp(accessable_from, accessable_hash))

master_password_hash = config.get("password", "master_password")
secret_code = config.get("password", "secret_code")


print("[checkpass] waiting for connection")
server_listener = UnixSocketListener(sock_path, apps)
server = server_listener.next_client()
print("[checkpass] someone connected successfully")

while True:
    command = server.read_line().split()

    if command[0] == "end":
        break
    if command[0] == "secret_code":
        print("[checkpass] sending secret_code to client")
        server.write_line(secret_code)
    elif command[0] == "check":
        print("[checkpass] checking if client code is correct")
        if SHA512.new(command[1]).hexdigest() == master_password_hash:
            server.write_line("1")
        else:
            server.write_line("0")
