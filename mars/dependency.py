"""
DepInfo: dependency data
DepMethod: a wrapper of a function with addtional __seq_num member
DepSolution: a container of DepMethod
Dependency: map a DepInfo with a specific DepSolution
"""
from . import downloader
import tarfile
import os.path
from . import logger


class DepInfo:
    def __init__(self, dep_info):
        self.name = dep_info["name"]
        self.addr = dep_info["addr"]
        self.dst_dir = dep_info.get("dst_dir", None)
        self.dst_name = dep_info.get("dst_name", None)
        self.__seq_num = dep_info.get("seq_num", 0)
        self.last_dep_method_ret = None

    def __lt__(self, other):
        return self.__seq_num < other.__seq_num


class DepMethod:
    def __init__(self, method, seq_num=0):
        self.__seq_num = seq_num
        self.__dep_method = method

    def set_seq_num(self, new_seq_num):
        self.__seq_num = new_seq_num

    def __call__(self, dep_info):
        self.__dep_method(dep_info)

    def __lt__(self, other):
        return self.__seq_num < other.__seq_num


def __fixer_download(dep_info):
    d = downloader.Downloader(dep_info.addr,
                              dep_info.dst_dir, dep_info.dst_name)
    retFile = d.start()
    lg = logger.Logger()
    lg.log("dependency @name: {0} has been downloaded."
           .format(dep_info.name))
    dep_info.last_dep_method_ret = retFile


def __fixer_extract(dep_info):
    file_name = dep_info.last_dep_method_ret
    if file_name is None:
        raise
    ext = file_name.split(".")[-1]
    if ext == "gz" or ext == "bz2" or ext == "xz":
        with tarfile.open(file_name) as f:
            old_cwd = os.getcwd()
            dst_dir = os.path.dirname(file_name)
            os.chdir(dst_dir)
            if not os.path.exists(dep_info.name):
                os.mkdir(dep_info.name)
            os.chdir(dep_info.name)
            f.extractall()
            lg = logger.Logger()
            lg.log("""\
dependency @name: {0} has been extracted, @path: \"{1}\"."""
                   .format(dep_info.name,
                           dst_dir + os.sep + dep_info.name))
            os.chdir(old_cwd)
    else:
        raise


class DepSolution:
    def __init__(self, *dep_methods):
        self.__dep_methods = list(dep_methods)

    def __call__(self, dep_info):
        self.__dep_methods.sort()
        for dm in self.__dep_methods:
            dm(dep_info)

    def add_method(self, dep_method):
        self.__dep_methods.append(dep_method)


default_dep_sln = DepSolution(DepMethod(__fixer_download, 0),
                              DepMethod(__fixer_extract, 1))

default_dep_sln.add_method = None  # disable further adding method


class Dependency:
    def __init__(self):
        self.__deps = {}

    def add(self, dep_info, dep_sln=None):
        if dep_sln is None:
            dep_sln = default_dep_sln
        self.__deps[dep_info] = dep_sln

    def get_solution(self, dep_info):
        return self.__deps[dep_info]

    def fix(self):
        sorted_deps = sorted(self.__deps.items(), key=lambda kv: kv[0])
        for kv in sorted_deps:
            kv[1](kv[0])
