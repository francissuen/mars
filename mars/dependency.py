"""
DepInfo: dependency data
DepMethod: a wrapper of a function with addtional __seq_num member
DepSolution: a container of DepMethod
Dependency: map a DepInfo with a specific DepSolution
"""
from . import downloader
import tarfile
import os.path
import subprocess
import shutil
from . import logger


class DepInfo:
    def __init__(self, dep_info):
        self.src_path = dep_info["src_path"]
        self.dst_path = dep_info.get("dst_path", None)
        self.seq_num = dep_info.get("seq_num", 0)
        self.last_dep_method_ret = None

    def __lt__(self, other):
        return self.seq_num < other.seq_num


def __fixer_download(dep_info):
    d = downloader.Downloader(dep_info.src_path,
                              dep_info.dst_path)
    retFile = d.start()
    lg = logger.Logger()
    lg.log("dependency @name: {0} has been downloaded."
           .format(retFile))
    dep_info.last_dep_method_ret = retFile


def __fixer_fs_git_proj_download_method(dep_info):
    old_cwd = os.getcwd()
    if not os.path.isdir("dep_tmp"):
        os.mkdir("dep_tmp")
    os.chdir("dep_tmp")

    dep_name = dep_info.src_path.split('/')[-1].split('.')[0]
    if dep_name is None or dep_name == '':
        raise
    if os.path.isdir(dep_name):
        os.chdir(dep_name)  # cd to target dir
        # git update local repository
        subprocess.run(["git", "pull", "origin", "master"])
    else:
        # clone git repository
        subprocess.run(["git", "clone", dep_info.src_path])
        os.chdir(dep_name)
        subprocess.run(["git", "checkout", "master"])    # TODO checkout master

    subprocess.run(["python3", "setup.py"])          # run setup.py
    shutil.copy("fsCMake/build.py", ".")
    subprocess.run(["python3", 'build.py', "-p"])

    dep_info.last_dep_method_ret = os.path.abspath(dep_name + ".tar.xz")
    os.chdir(old_cwd)

    
def __fixer_extract_here(dep_info):
    tar_file_path = dep_info.last_dep_method_ret
    if tar_file_path is None:
        raise
    if dep_info.dst_path is None:
        dep_info.dst_path = os.getcwd()
        print(os.getcwd())
    if os.path.isdir(dep_info.dst_path):
        dst_dir = dep_info.dst_path
    else:
        dst_dir = os.path.dirname(dep_info.dst_path)
    if dst_dir is None:
        raise
    
    if tarfile.is_tarfile(tar_file_path):
        with tarfile.open(tar_file_path) as f:
            old_cwd = os.getcwd()
            os.chdir(dst_dir)
            f.extractall()
            os.chdir(old_cwd)
            lg = logger.Logger()
            lg.log("""\
dependency @name: {0} has been extracted."""
                   .format(tar_file_path))
    else:
        raise


class DepSolution:
    def __init__(self, *dep_methods):
        if dep_methods is None:
            raise
        self.__dep_methods = {}
        for dm in dep_methods:
            if not isinstance(dm, dict):
                raise
            self.__dep_methods[dm["seq_num"]] = dm["fixer"]

    def __call__(self, dep_info):
        sorted_dms = sorted(self.__dep_methods.items(), key=lambda kv: kv[0])
        for dm in sorted_dms:
            dm[1](dep_info)

    def add_method(self, dep_method):
        self.__dep_methods.append(dep_method)


default_dep_sln = DepSolution({"seq_num": 0, "fixer": __fixer_download},
                              {"seq_num": 1, "fixer": __fixer_extract_here})

default_dep_sln.add_method = None  # disable further adding method

fs_git_proj_dep_sln = DepSolution({"seq_num": 0, "fixer":
                                   __fixer_fs_git_proj_download_method},
                                  {"seq_num": 1, "fixer":
                                   __fixer_extract_here})

fs_git_proj_dep_sln.add_method = None


class Dependency:
    def __init__(self, root_dir=None, third_party_dir=None):
        self.__deps = {}
        if root_dir is None:
            self.__root_dir = os.getcwd()
        if third_party_dir is None:
            self.__third_party_dir = "thirdParty"

        if not os.path.isdir(self.__third_party_dir):
            os.mkdir(self.__third_party_dir)

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
