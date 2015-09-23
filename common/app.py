class SingleApp():
    def __init__(self, executable, exec_hash):
        self.executable = executable
        self.exec_hash = exec_hash

    def __eq__(self, other):
        if isinstance(other, SingleApp):
            return other.executable == self.executable and self.exec_hash == other.exec_hash
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
