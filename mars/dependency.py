"""
DepInfo: dependency data (NOTE when src_path is a git repository address, then
src_path is composited with two parts, which are repository address and branch
name, sperated by a whitespace. If the 2nd part is elided then the default
branch name "master" will be used.)
DepMethod: a wrapper of a function with addtional __seq_num member
DepSolution: a container of DepMethod
Dependency: map a DepInfo to a DepSolution
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
        self.dst_dir = dep_info.get("dst_dir", None)
        self.seq_num = dep_info.get("seq_num", 0)
        self.last_dep_method_ret = None

    def __lt__(self, other):
        return self.seq_num < other.seq_num


def __fixer_download(dep_info):
    d = downloader.Downloader(dep_info.src_path,
                              dep_info.dst_dir)
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

    src_info = dep_info.src_path.split(' ')
    src_path = src_info[0]
    src_branch = "master"
    if len(src_info) > 1:
        src_branch = src_info[1]

    dep_name = src_path.split('/')[-1].split('.')[0]
    if dep_name is None or dep_name == '':
        raise
    if os.path.isdir(dep_name):
        os.chdir(dep_name)  # cd to target dir
        # first checkout src_branch
        subprocess.run(["git", "checkout", src_branch])
        # update local repository
        subprocess.run(["git", "pull", "origin", src_branch])
    else:
        # clone git repository
        subprocess.run(["git", "clone", src_path])
        os.chdir(dep_name)
        subprocess.run(["git", "checkout", src_branch]
                       )    # TODO checkout src_branch

    if os.path.isfile("setup.py"):
        subprocess.run(["python3", "setup.py"])          # run setup.py

    if os.path.isfile("vesta/build.py"):
        # build a pkg tar file
        shutil.copy("vesta/build.py", ".")
        subprocess.run(["python3", 'build.py', "-p"])

        # set last_dep_method_ret for next step
        dep_info.last_dep_method_ret = os.path.abspath(dep_name + ".tar.xz")
    else:
        # copy this repository to dep_info.dst_dir
        if dep_info.dst_dir is None:
            dst_dir = old_cwd
        else:
            dst_dir = dep_info.dst_dir

        # append dep_name to dst_dir
        dst_dir = os.path.join(dst_dir, dep_name)    
        # rm dst_dir if it exists
        if os.path.isdir(dst_dir):
            shutil.rmtree(dst_dir)
        # copy
        shutil.copytree(".", dst_dir)

    os.chdir(old_cwd)


def __fixer_extract_here(dep_info):
    tar_file_path = dep_info.last_dep_method_ret
    if tar_file_path is None:
        return
    if dep_info.dst_dir is None:
        dst_dir = os.getcwd()
    else:
        dst_dir = dep_info.dst_dir

    if not os.path.isdir(dst_dir):
        os.makedirs(dst_dir)

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
    def __init__(self, root_dir=None):
        self.__deps = {}
        if root_dir is None:
            self.__root_dir = os.getcwd()

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
