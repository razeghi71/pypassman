from socket import socket, AF_UNIX, SOCK_STREAM, SOL_SOCKET
from proc.core import Process
import struct
import filehash
import os.path
from common.app import SingleApp
from common.db import App
from api.api import API


class InvalidAppConnectException(Exception):

    def __init__(self):
        pass

    def __str__(self):
        return "Invalid App Connected To Password Getter"


class BaseUnixSocket():

    MAX_SIZE = 1024

    def __init__(self, path):
        self.s = None

    def read_line(self):
        buffer = ''
        delim = '\n'
        data = True
        while data:
            data = self.s.recv(self.MAX_SIZE)
            buffer += data

            while buffer.find(delim) != -1:
                line, buffer = buffer.split('\n', 1)
                return line
        return

    def write_line(self, send_str):
        self.s.send(send_str + '\n')

    def disconnect(self):
        self.s.close()


class UnixSocketClient(BaseUnixSocket):

    SO_PASSCRED = 16

    def __init__(self, path):
        self.s = socket(AF_UNIX, SOCK_STREAM)
        self.s.setsockopt(SOL_SOCKET, self.SO_PASSCRED, 1)
        self.s.connect(path)


class UnixSocketServer(BaseUnixSocket):

    def __init__(self, s, addr, app):
        self.s = s
        self.addr = addr
        self.app = app


class UnixSocketListener():
    LISTEN_BACKLOG = 100
    SO_PEERCRED = 17

    def __init__(self, path, client_apps=None, approver=None):
        self.client_apps = client_apps
        if os.path.exists(path):
            os.remove(path)
        self.server = socket(AF_UNIX, SOCK_STREAM)
        self.server.bind(path)
        os.chmod(path, 0o777)
        self.server.listen(self.LISTEN_BACKLOG)
        self.extra_approver = approver

    def next_client(self):
        s, addr = self.server.accept()
        verified, connected_app = self.verify_app(s)
        server_sock = UnixSocketServer(s, addr, connected_app)
        if not verified:
            server_sock.disconnect()
            return None
        return server_sock

    def verify_app(self, s):
        creds = s.getsockopt(
            SOL_SOCKET, self.SO_PEERCRED, struct.calcsize('3i'))
        pid, uid, gid = struct.unpack('3i', creds)

        proc = Process.from_pid(pid)
        file_hash = filehash.file_sha1(proc.exe)
        connected_app = SingleApp(proc.exe, file_hash)

        if (self.client_apps and connected_app in self.client_apps)  \
                or self.extra_approver(connected_app):
            return True, connected_app

        return False, None
