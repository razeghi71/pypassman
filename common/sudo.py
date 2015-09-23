import subprocess

def run_command(command):
    print("[sudo.py] running " + command + " ...")
    subprocess.Popen(command.split())


def sudo_user_group(user, group, command):
    return ('sudo -u %s -g %s %s' % (user, group, command))


def sudo_user(user, command):
    return ('sudo -u %s %s' % (user, command))


def sudo_group(group, command):
    return ('sudo -g %s %s' % (group, command))


def sudo(command):
    return ('sudo %s' % (command))


def get_command_openvt(command):
    return sudo('openvt -f -w -s -c 23 -- %s' % command)
