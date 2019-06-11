from . import __url
import threading


def pick_downloader(src):
    # TODO
    return __url.downloader


class Downloader:
    def __init__(self, src_path, dst_path=None):
        self.__downloader = pick_downloader(src_path)
        self.__src_path = src_path
        self.__dst_path = dst_path

    def start(self):
        return self.__downloader(self.__src_path, self.__dst_path)


class AsyncDownloader(threading.Thread):
    def __init__(self, src_path, dst_path=None):
        super(AsyncDownloader, self).__init__()
        self.__Downloader = Downloader(src_path, dst_path)

    def run(self):
        d = self.__Downloader
        d.__downloader.start()
