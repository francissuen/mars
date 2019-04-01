from . import __url
import threading


def pick_downloader(addr):
    # TODO
    return __url.downloader


class Downloader:
    def __init__(self, addr):
        self.__downloader = pick_downloader(addr)
        self.__addr = addr

    def start(self):
        self.__downloader(self.__addr)


class DownloaderAsync(threading.Thread):
    def __init__(self, addr):
        super(DownloaderAsync, self).__init__()
        self.__downloader = pick_downloader(addr)
        self.__addr = addr

    def run(self):
        self._downloader(self.__addr)
