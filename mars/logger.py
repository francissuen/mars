from sys import stdout
import time


class Logger:
    def __init__(self, fd=None):
        if fd is None:
            self.fd = stdout
        self.log = lambda msg: self.fd.write(
            time.asctime() + "\n" + msg + "\n")
