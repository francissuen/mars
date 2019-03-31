import urllib.request
import sys
import numbers
import time
import threading
import os


def fancy_bytes_format(bytes):
    if not isinstance(bytes, numbers.Number):
        return
    KB = 1024
    MB = 1024 * KB
    G = 1024 * MB
    unit, scale = "B", bytes
    if bytes > G:
        unit = "G"
        scale = bytes / G
    elif bytes > MB:
        unit = "MB"
        scale = bytes / MB
    elif bytes > KB:
        unit = "KB"
        scale = bytes / KB
    return "{0:06.2f} {1}".format(scale, unit)


def rm_url_trailing_trash_characters(raw_url):
    trash_characters = "\n "
    endOfUrlIdx = -1
    for i in range(-1, -len(raw_url), -1):
        if trash_characters.count(raw_url[i]) == 0:
            endOfUrlIdx = i + 1  # include last one
            break
    return raw_url[0:endOfUrlIdx]


class Logger:
    def __init__(self):
        pass

    def log(msg):
        sys.stdout.write(time.asctime() + "\n" + msg + "\n")


def download_file(url):
    url = rm_url_trailing_trash_characters(url)
    if len(url) == 0:
        return
    file_name = url.split('/')[-1]
    if len(file_name) == 0:
        return
    print(url)
    # open url
    with urllib.request.urlopen(url) as response:
        # info of file
        content_len = int(response.getheader("Content-Length"))
        Logger.log("file @name: {0}, @size: {1}".format(
            file_name, fancy_bytes_format(content_len)))
        # download procedure
        sizeOfWritten = 0
        tmp_file_name = file_name + ".tmp"
        with open(tmp_file_name, "wb") as f:
            for i in range(0, content_len, 1024):
                # data[0:1024] = response.read(1024)
                data = response.read(1024)
                sizeOfWritten += len(data)
                f.write(data)
                sys.stdout.write("@size: {0}\r"
                                 .format(fancy_bytes_format(sizeOfWritten)))
                sys.stdout.flush()

            f.flush()
            os.rename(tmp_file_name, file_name)
            sys.stdout.write("written to file @name: {0}\n".format(file_name))
            sys.stdout.flush()


class File_downloader(threading.Thread):
    def __init__(self, url):
        super(File_downloader, self).__init__()
        self.url = url

    def run(self):
        download_file(self.url)


# http://mirrors.us.kernel.org/ubuntu-releases/18.04.2/ubuntu-18.04.2-live-server-amd64.iso
# https://github.com/francissuen/fsCMake/releases/download/v1.0.3/fsCMake.tar.xz
url = """\
http://mirrors.us.kernel.org/ubuntu-releases/18.04.2/ubuntu-18.04.2-live-server-amd64.iso
"""
fd = File_downloader(url)

fd.start()

fd.join()

# dependencies =
# [
#     ""
# ]
