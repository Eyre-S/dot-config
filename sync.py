from genericpath import exists
from typing import Iterable
from enum import Enum
from math import nan
import os
from os import path
from pathlib import Path


backup_root: str = path.dirname(__file__)
user_home: str = path.expanduser("~")

if user_home == "~":
    print("WARN: Cannot read the user home dir, do you run it in the correct script?")
    print("continue? [y/N]")
    if (input().lower != 'y'):
        exit()
else:
    print("dot-config: current user home: " + user_home)

def sorted_paths (paths: Iterable[str]) -> list[str]:
    fin = sorted(paths)
    return fin

def de_abs_path (path: str) -> str:
    return path.strip('/').strip('\\')

class BackupItem:
    def __init__ (self, backup_dir: str, origin_dir: str) -> None:
        self.name: str = backup_dir
        self.backup_dir: str = path.join(backup_root, backup_dir)
        self.origin_dir: str = path.abspath(path.expanduser(origin_dir))

table: list[BackupItem] = [
    BackupItem("PowerShell", "~/Documents/PowerShell")
]

def execute_sync (backupItem: BackupItem) -> None:
    print(f">>> executing backup for {backupItem.name}")
    all_files_tmp: list[str] = []
    def walk_dir (walking_dir: str):
        for root, dirs, files in os.walk(walking_dir):
            common_root: str = path.commonpath([root, walking_dir])
            if common_root == walking_dir:
                relative_root: str = root[len(walking_dir):]
            else:
                print(f"WARN: cannot find common root for {root} and {walking_dir}, will break this dir.")
                continue 
            for file in files:
                relative_file_path = de_abs_path(path.join(relative_root, file))
                # print(f"find file in source: {`relative_file_path`}")
                all_files_tmp.append(relative_file_path)
    walk_dir(backupItem.origin_dir)
    walk_dir(backupItem.backup_dir)
    all_files: list[str] = sorted_paths(set(all_files_tmp))
    for file in all_files:
        compare_file(backupItem, file)
    # print("\n".join(all_files))

def compare_file (rootBackItem: BackupItem, relative_file_path: str) -> None:
    class IsNewerStatus (Enum):
        OLDER = -1
        NEWER = 1
        DIFFERENT = nan
        SAME = 0
    class FileStatus:
        def __init__(self, realpath: str) -> None:
            self.path = realpath
            self.exists = path.exists(realpath)
            if self.exists:
                self.size = path.getsize(realpath)
                self.edited_time = path.getmtime(realpath)
        def isNewerThan (self, other):
            # type: (FileStatus) -> IsNewerStatus
            if not self.exists:
                return IsNewerStatus.OLDER
            if not other.exists:
                return IsNewerStatus.NEWER
            if self.edited_time > other.edited_time:
                return IsNewerStatus.NEWER
            elif self.edited_time < other.edited_time:
                return IsNewerStatus.OLDER
            if self.size != other.size:
                return IsNewerStatus.DIFFERENT
            return IsNewerStatus.SAME
    backup_item: FileStatus = FileStatus(path.join(rootBackItem.backup_dir, relative_file_path))
    origin_item: FileStatus = FileStatus(path.join(rootBackItem.origin_dir, relative_file_path))
    match origin_item.isNewerThan(backup_item):
        case IsNewerStatus.SAME:
            print(f"{relative_file_path} : is same")
        case IsNewerStatus.OLDER:
            print(f"{relative_file_path} : backup file is newer")
        case IsNewerStatus.NEWER:
            print(f"{relative_file_path} : original file is newer")
        case IsNewerStatus.DIFFERENT:
            print(f"{relative_file_path} : WARN : backup is different but cannot determine which is newer")

for i in table:
    execute_sync(i)
