from . import downloader
import tarfile
import os.path


class Dependency:
    def __fixer_download(self):
        d = downloader.Downloader(self.__addr, self.__dst_dir, self.__dst_name)
        return d.start()

    def __fixer_extract(self, file_name):
        ext = file_name.split(".")[-1]
        if ext == "gz" or ext == "bz2" or ext == "xz":
            with tarfile.open(file_name) as f:
                old_cwd = os.getcwd()
                os.chdir(os.path.dirname(file_name))
                if not os.path.exists(self.__name):
                    os.mkdir(self.__name)
                os.chdir(self.__name)
                f.extractall()
                os.chdir(old_cwd)
        else:
            raise

    def __fixer_default(self):
        # self.__fixer_download()
        self.__fixer_extract(self.__fixer_download())

    __fixer_sets = {"d": __fixer_download,
                    "x": __fixer_extract}

    def __init__(self, dep_info):
        self.__name = dep_info["name"]
        self.__addr = dep_info["addr"]
        self.__dst_dir = dep_info.get("dst_dir", None)
        self.__dst_name = dep_info.get("dst_name", None)
        self.__fixer = dep_info.get("fixer", self.__fixer_default)
        if isinstance(self.__fixer, str):
            self.__fixer = self.__fixer_sets[self.__fixer]

    def fix(self):
        return self.__fixer()
