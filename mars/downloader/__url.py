import urllib.request
import sys
import numbers
import os
import os.path
from .. import logger


def fancy_bytes_format(size_in_b):
    if not isinstance(size_in_b, numbers.Number):
        return
    KB = 1024
    MB = 1024 * KB
    G = 1024 * MB
    unit, scale = "B", size_in_b
    if size_in_b > G:
        unit = "G"
        scale = size_in_b / G
    elif size_in_b > MB:
        unit = "MB"
        scale = size_in_b / MB
    elif size_in_b > KB:
        unit = "KB"
        scale = size_in_b / KB
    return "{0:06.2f} {1}".format(scale, unit)


def rm_url_trash_characters(raw_url):
    trash_characters = "\n "
    ret = ""
    for c in raw_url:
        if trash_characters.count(c) == 0:
            ret += c
    return ret


def downloader(url, dst_dir=None, dst_name=None):
    url = rm_url_trash_characters(url)
    if len(url) == 0:
        return None

    if dst_dir is None:
        abs_dst_dir = os.getcwd()
    else:
        abs_dst_dir = os.path.abspath(dst_dir)
        if not os.path.isdir(abs_dst_dir):
            os.mkdir(abs_dst_dir)

    if dst_name is None:
        file_name = url.split('/')[-1]
    else:
        file_name = dst_name

    file_name = abs_dst_dir + os.sep + file_name

    if len(file_name) == 0:
        return None

    # open url
    with urllib.request.urlopen(url) as response:
        # info of file
        content_len = int(response.getheader("Content-Length"))
        log = logger.Logger()
        log.log("file @name: {0}, @size: {1}".format(
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
            sys.stdout.flush()
            return file_name


# usage
# url = """\
# http://mirrors.us.kernel.org/ubuntu-releases/18.04.2/ubuntu-18.04.2-live-server-amd64.iso
# """
# d = Downloader(url)

# d.start()

# d = DownloaderAsync(url)
# d.start()
# d.join()
