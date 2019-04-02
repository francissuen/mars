from . import __url
import threading


def pick_downloader(src):
    # TODO
    return __url.downloader


class Downloader:
    def __init__(self, src, dst_dir=None, dst_name=None):
        self.__downloader = pick_downloader(src)
        self.__src = src
        self.__dst_dir = dst_dir
        self.__dst_name = dst_name

    def start(self):
        return self.__downloader(self.__src, self.__dst_dir, self.__dst_name)


class DownloaderAsync(threading.Thread):
    def __init__(self, src, dst_dir=None, dst_name=None):
        super(DownloaderAsync, self).__init__()
        self.__Downloader = Downloader(src, dst_dir, dst_name)

    def run(self):
        d = self.__Downloader
        d.__downloader.start()
