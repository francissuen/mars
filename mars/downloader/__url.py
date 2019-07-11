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


def downloader(url, dst_path=None):
    url = rm_url_trash_characters(url)
    if len(url) == 0:
        return None

    if dst_path is None:
        dst_path = url.split('/')[-1]
    elif dst_path != '':
        # make dir if not exists
        dst_dir = os.path.dirname(dst_path)
        if dst_dir is None:
            return None
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        filename = os.path.basename(dst_path)
        if filename is None:
            filename = url.split('/')[-1]
            dst_path = os.path.join(dst_dir, filename)
    else:
        return None

    if dst_path is None or dst_path == '':
        return None

    # open url
    with urllib.request.urlopen(url) as response:
        # info of file
        content_len = int(response.getheader("Content-Length"))
        log = logger.Logger()
        log.log("file @name: {0}, @size: {1}".format(
            dst_path, fancy_bytes_format(content_len)))
        # download procedure
        sizeOfWritten = 0
        tmp_file_name = dst_path + ".tmp"
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
            f.close()
            if os.path.isfile(dst_path):
                os.remove(dst_path)
            os.rename(tmp_file_name, dst_path)
            sys.stdout.flush()
            return dst_path


# usage
# url = """\
# http://mirrors.us.kernel.org/ubuntu-releases/18.04.2/ubuntu-18.04.2-live-server-amd64.iso
# """
# d = Downloader(url)

# d.start()

# d = DownloaderAsync(url)
# d.start()
# d.join()
