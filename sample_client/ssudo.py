from common.connection import UnixSocketClient
from optparse import OptionParser
from common.sudo import run_command
from exceptions import KeyError
from subprocess import Popen, PIPE
import getpass
import argparse
import sys
import shelve


d = shelve.open("id.shelve")

api_path = "/tmp/passman_api"

client = UnixSocketClient(api_path)

# parser = argparse.ArgumentParser()
# parser.add_argument("-u")
# args = parser.parse_args()

username = "root"

if "-u" in sys.argv:
    i = sys.argv[1:].index("-u")
    username = sys.argv[i+1]

if "--user" in sys.argv:
    i = sys.argv[1:].index("--user")
    username = sys.argv[i+1]

try:
    saved_id = d[username]
    client.write_line("get %s" % saved_id)
    _ , saved_id, username, password = client.read_line().split()
except KeyError:
    password = getpass.getpass()
    client.write_line("save %s %s" % (username, password))
    id = client.read_line().split()[1]
    d[username] = id

client.write_line("end")
client.disconnect()
d.close()

nosudo_command = " ".join(sys.argv[1:])
command = ("sudo -S %s" % (nosudo_command)).split()

p = Popen(['sudo', '-S'] + command, stdin=PIPE,
          universal_newlines=True)

sudo_prompt = p.communicate(password + '\n')[1]
