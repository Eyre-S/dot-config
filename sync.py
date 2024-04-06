from turtle import back
from typing import Callable, Iterable, TypeVar
from enum import Enum
from math import nan
import os
from os import path
import sys
import shutil

#=== Global Parameters ===#
dry_run: bool = False

#=== Utils ===#
import re
import hashlib

T_WaitForInput_Res = TypeVar('T_WaitForInput_Res')
def wait_for_input (cb: Callable[[str], T_WaitForInput_Res|None]) -> T_WaitForInput_Res:
    while True:
        _in = input()
        _out = cb(_in)
        if _out != None:
            return _out

def replace_env_variables(input_string):
    """
    Replaces environment variables in the input string with their current values.
    """
    def replace_env(match):
        env_var = match.group(1)
        return os.environ.get(env_var, f"${{{env_var}}}")

    # Use regular expression to find environment variable placeholders
    pattern = r"%(\w+)%"
    replaced_string = re.sub(pattern, replace_env, input_string)
    return replaced_string

def sorted_paths (paths: Iterable[str]) -> list[str]:
    fin = sorted(paths)
    return fin

def de_abs_path (path: str) -> str:
    return path.strip('/').strip('\\')

def get_file_hash(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        bytes = f.read()  # read entire file as bytes
        readable_hash = hashlib.md5(bytes).hexdigest()
        return readable_hash

def ensure_file_dir (file_path: str) -> None:
    dir: str = path.dirname(file_path)
    if dir != '' and not path.exists(dir):
        if not dry_run:
            os.makedirs(dir)
        print(f":created parent dir {dir}")

def copyfile (src: str, dest: str) -> None:
    ensure_file_dir(dest)
    if not dry_run:
        shutil.copy2(src, dest)
    print(f":copied {src} -> {dest}")
    print(f":updated {dest}")

def delfile (file_path: str) -> None:
    if not dry_run:
        os.remove(file_path)
    print(f":deleted {file_path}")

#=== Backup Item ===#

class BackupItem:
    def __init__ (self, backup_dir: str, origin_dir: str) -> None:
        self.name: str = backup_dir
        self.backup_dir: str = path.join(backup_root, backup_dir)
        self.origin_dir: str = path.abspath(replace_env_variables(path.expanduser(origin_dir)))

def execute_sync (backupItem: BackupItem) -> None:
    print(f">>> executing backup for {backupItem.name}")
    all_files_tmp: list[str] = []
    ### for file mode
    if (path.isfile(backupItem.origin_dir)) or (path.isfile(backupItem.backup_dir)):
        compare_file(backupItem, None)
    ### for dir mode
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
    exec_gallery: list[Callable] = []
    for file in all_files:
        exec_gallery.append(compare_file(backupItem, file))
    while True:
        print("! sync those files now? [y/n] ", end="")
        _in = input()
        if _in == 'y':
            for i in exec_gallery:
                i()
            return
        elif _in == 'n':
            return
        else:
            print("! sync those files now? [y/n] ", end="")

def compare_file (rootBackItem: BackupItem, relative_file_path: str|None) -> Callable:
    class NewerStatus (Enum):
        RIGHT_MISSING = -2
        RIGHT_OLDER = -1
        LEFT_OLDER = 1
        LEFT_MISSING = 2
        DIFFERENT = nan
        ALL_MISSING = -999
        SAME = 0
    class FileStatus:
        def __init__ (self, realpath: str) -> None:
            self.path = realpath
            self.exists = path.exists(realpath)
            if self.exists:
                self.size = path.getsize(realpath)
                self.edited_time = path.getmtime(realpath)
        def hash_of_file (self) -> str:
            if not self.exists:
                return ""
            return get_file_hash(self.path)
    def FileSameCheck (left: FileStatus, right: FileStatus) -> NewerStatus:
        def check_hash_same_or (status: NewerStatus) -> NewerStatus: # TODO: add to compare
            if left.hash_of_file() == right.hash_of_file():
                return NewerStatus.SAME
            return status
        if not left.exists:
            if not right.exists:
                return NewerStatus.ALL_MISSING
            return NewerStatus.LEFT_MISSING
        if not right.exists:
            if not left.exists:
                return NewerStatus.ALL_MISSING
            return NewerStatus.RIGHT_MISSING
        if left.edited_time > right.edited_time:
            return NewerStatus.LEFT_OLDER
        elif left.edited_time < right.edited_time:
            return NewerStatus.RIGHT_OLDER
        if left.size != right.size:
            return NewerStatus.DIFFERENT
        return NewerStatus.SAME
    if relative_file_path == None:
        backup_item: FileStatus = FileStatus(rootBackItem.backup_dir)
        origin_item: FileStatus = FileStatus(rootBackItem.origin_dir)
        file_id: str = rootBackItem.name
    else:
        backup_item: FileStatus = FileStatus(path.join(rootBackItem.backup_dir, relative_file_path))
        origin_item: FileStatus = FileStatus(path.join(rootBackItem.origin_dir, relative_file_path))
        file_id: str = relative_file_path
    # print(f"((backup_item: {backup_item.path}))")
    # print(f"((origin_item: {origin_item.path}))")
    def wait_for_if_remove (onSync = Callable, onRemove = Callable) -> Callable[[str], Callable|None]:
        def implementation (_in: str) -> Callable|None:
            
            while True:
                _in = input()
                match _in:
                    case "s":
                        return onSync
                    case "r":
                        return onRemove
                    case "i":
                        return lambda: None
                    case _:
                        print("sync or remove? [s=sync/r=remove/i=ignore] ", end="")
                        return None
        return implementation
    match FileSameCheck(origin_item, backup_item):
        case NewerStatus.SAME:
            # print(f"{file_id} : is same")
            pass
        case NewerStatus.RIGHT_OLDER:
            print(f"{file_id} : local file is newer")
            return lambda: copyfile(origin_item.path, backup_item.path)
        case NewerStatus.LEFT_OLDER:
            print(f"{file_id} : backup file is newer")
            return lambda: copyfile(backup_item.path, origin_item.path)
        case NewerStatus.RIGHT_MISSING:
            print(f"{file_id} : backup file is missing, sync or remove? [s=sync/r=remove/i=ignore] ", end="")
            return wait_for_input(wait_for_if_remove(
                onSync = lambda: copyfile(origin_item.path, backup_item.path),
                onRemove = lambda: delfile(origin_item.path)
            ))
        case NewerStatus.LEFT_MISSING:
            print(f"{file_id} : local file is missing, sync or remove? [s=sync/r=remove/i=ignore] ", end="")
            exec = wait_for_input(wait_for_if_remove(
                onSync = lambda: copyfile(backup_item.path, origin_item.path),
                onRemove = lambda: delfile(backup_item.path)
            ))
            return exec
        case NewerStatus.DIFFERENT:
            print(f"{file_id} : backup is different with local, which to keep? [b=backup/l=local/i=ignore] ", end="")
            return wait_for_input(lambda _in: (
                (lambda: copyfile(backup_item.path, origin_item.path)) if _in == 'l' else
                (lambda: copyfile(origin_item.path, backup_item.path)) if _in == 'b' else
                (lambda: None) if _in == 'i' else
                None
            ))
        case NewerStatus.ALL_MISSING:
            print(f"{file_id} : both files are missing, will skipped")
    return lambda: None

#=== Init ===#

for i in sys.argv:
    if i == "--help" or i == '-h':
        print("Usage: sync.py")
        print("   -n --dry-run : enable dry-run mode")
        print("   -v --version : show version")
        print("   -h --help    : show this help")
        exit()
    if i == "--version" or i == '-v':
        print("dot-config sync.py v1.annie.0-alpha1")
        exit()
    if i == '--dry-run' or i == '-n':
        dry_run = True
        print("dot-config: global dry-run mode enabled!")

backup_root: str = path.dirname(__file__)
user_home: str = path.expanduser("~")

if user_home == "~":
    print("FATAL: Cannot read the user home dir, do you run it in the correct script?")
    exit()
else:
    print("dot-config: current user home: " + user_home)

class SysType (Enum):
    LINUX = 'linux'
    TERMUX = 'termux'
    WINDOWS = 'windows'
if ("termux" in backup_root):
    sys_type: SysType = SysType.TERMUX
elif (backup_root[0] == "/"):
    sys_type: SysType = SysType.LINUX
else:
    sys_type: SysType = SysType.WINDOWS
print(f"dot-config: your dot-config path is {backup_root}")
print(f"dot-config: your system type is {sys_type}")
print(f"Is all the information correct? [y/n] ", end="")
while True:
    _in = input()
    match _in:
        case "y":
            print("continuing...")
            break;
        case "n":
            print("Exiting")
            exit()
        case _:
            print("please confirm with [y/n] ", end="")

#=== main ===#
import json

table: list[BackupItem] = []
config_file = path.join(backup_root, f"sync.{sys_type.value}.json")
if not path.isfile(config_file):
    print(f"dot-config : FATAL : cannot find config file for current system in {config_file}")
    exit()
with open(config_file, 'r') as config_file_raw:
    config = json.load(config_file_raw)
    for i in config['backups']:
        here: str = i['path']
        there: str = i['source']
        print(f"-- loaded [{here}] <-> [{there}]")
        table.append(BackupItem(here, there))

print()
for i in table:
    # print(f"((BackupItem i : {i.name}))")
    # print(f"((i.backup_dir : {i.backup_dir}))")
    # print(f"((i.origin_dir : {i.origin_dir}))")
    execute_sync(i)
    print()
