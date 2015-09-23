from common.connection import UnixSocketListener
from thread import start_new_thread
from api import API


class APIListener():

    def __init__(self, path_sock, master_password, approver):
        self.listener = UnixSocketListener(path=path_sock, approver=approver)
        API().set_key(master_password)

    def run(self):
        self.listen_loop()

    def listen_loop(self):
        while True:
            sock = self.listener.next_client()
            start_new_thread(self.handle_client, (sock,))

    def handle_client(self, socket):

        while True:
            line = socket.read_line().split()
            if line[0] == "end":
                return
            elif line[0] == "save":
                ret_id = API().save_password(socket.app, line[1], line[2])
                socket.write_line("save %d" % ret_id)
            elif line[0] == "get":
                ret_id, username, password = API().get_password(socket.app, line[1])
                socket.write_line("get %d %s %s" % (ret_id, username, password))
            else:
                print("Invalid Command Recieved")
        
