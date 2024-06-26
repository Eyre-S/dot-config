from typing import Callable, Generic, Iterable, Literal, TypeVar
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

class _GetCh:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self) -> None:
        try:
            self.impl = _GetChWindows()
        except ImportError:
            self.impl = _GetChUnix()

    def __call__(self) -> str:
        return self.impl()
class _GetChUnix:
    def __init__(self) -> None:
        import tty, sys
    def __call__(self) -> str:
        import sys, tty, termios
        fd: int = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch: str = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
class _GetChWindows:
    def __init__(self) -> None:
        import msvcrt
    def __call__(self) -> str:
        import msvcrt
        return msvcrt.getch().decode('utf-8')
input_char = _GetCh()

T_Capsule = TypeVar('T_Capsule')
class Capsule (Generic[T_Capsule]):
    def __init__ (self, value: T_Capsule) -> None:
        self.value: T_Capsule = value

T_WaitForInput_Res = TypeVar('T_WaitForInput_Res')
def wait_for_input (cb: Callable[[str], Capsule[T_WaitForInput_Res]|None]) -> T_WaitForInput_Res:
    while True:
        sys.stdout.flush()
        _in = input_char()
        print()
        _out: Capsule[T_WaitForInput_Res]|None = cb(_in)
        if _out is not None:
            return _out.value

def wait_for_y_or_n_res (_in: str) -> Capsule[Literal['y', 'n']]|None:
    if _in == 'y' or _in == 'n':
        return Capsule(_in)
    print("please confirm with [y/n] ", end="")
    return None

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
        self.exclude: list[str] = []
    def add_exclude (self, exclude: str) -> None:
        self.exclude.append(exclude)

def execute_sync (backupItem: BackupItem) -> None:
    print(f">>> executing backup for {backupItem.name}")
    all_files: list[str|None] = []
    ### get files: for file mode
    if (path.isfile(backupItem.origin_dir)) or (path.isfile(backupItem.backup_dir)):
        all_files.append(None)
    ### get files: for dir mode
    else:
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
        all_files_tmp_2 = sorted_paths(set(all_files_tmp))
        for file in all_files_tmp_2:
            skip: bool = False
            for ex in backupItem.exclude:
                if re.match(ex, file) is not None:
                    skip = True
            if skip is True:
                # print(f"ignored:{file}")
                continue
            # print(f"syncing:{file}")
            all_files.append(file)
    ### process files rule
    exec_gallery: list[Callable|None] = []
    for file in all_files:
        exec_gallery.append(compare_file(backupItem, file))
    ### process
    exec_gallery_filtered: list[Callable] = []
    for (i) in exec_gallery:
        if i is not None:
            exec_gallery_filtered.append(i)
    if exec_gallery_filtered.__len__() == 0:
        print("no files to sync ~")
        return
    print("! sync those files now? [y/n] ", end="")
    match wait_for_input(wait_for_y_or_n_res):
        case "y":
            for i in exec_gallery_filtered:
                i()
        case "n":
            print("! skipped")

def compare_file (rootBackItem: BackupItem, relative_file_path: str|None) -> Callable|None:
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
            return check_hash_same_or(NewerStatus.RIGHT_OLDER)
        elif left.edited_time < right.edited_time:
            return check_hash_same_or(NewerStatus.LEFT_OLDER)
        if left.size != right.size:
            return NewerStatus.DIFFERENT
        return NewerStatus.SAME
    if relative_file_path is None:
        backup_item: FileStatus = FileStatus(rootBackItem.backup_dir)
        origin_item: FileStatus = FileStatus(rootBackItem.origin_dir)
        file_id: str = rootBackItem.name
    else:
        backup_item: FileStatus = FileStatus(path.join(rootBackItem.backup_dir, relative_file_path))
        origin_item: FileStatus = FileStatus(path.join(rootBackItem.origin_dir, relative_file_path))
        file_id: str = relative_file_path
    # print(f"((backup_item: {backup_item.path}))")
    # print(f"((origin_item: {origin_item.path}))")
    def wait_for_if_remove (onSync = Callable, onRemove = Callable) -> Callable[[str], Capsule[Callable|None]|None]:
        def implementation (_in: str) -> Capsule[Callable|None]|None:
            match _in:
                case "s":
                    return Capsule(onSync)
                case "r":
                    return Capsule(onRemove)
                case "i":
                    return Capsule(None)
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
            return wait_for_input((wait_for_if_remove(
                onSync = lambda: copyfile(origin_item.path, backup_item.path),
                onRemove = lambda: delfile(origin_item.path)
            )))
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
                Capsule((lambda: copyfile(backup_item.path, origin_item.path))) if _in == 'l' else
                Capsule((lambda: copyfile(origin_item.path, backup_item.path))) if _in == 'b' else
                Capsule(None) if _in == 'i' else
                None
            ))
        case NewerStatus.ALL_MISSING:
            print(f"{file_id} : both files are missing, will skipped")
    return None

def load_config () -> list[BackupItem]:
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
            curr = BackupItem(here, there)
            if 'exclude' in i:
                exclude: list[str] = i['exclude']
                print("   > excludes: (%s)"%(", ".join(map(lambda x: f"\"{x}\"", exclude))))
                # print(f"   > excludes: ({(", ".join(map(lambda x: f"\"{x}\"", exclude)))})")
                for ex in exclude:
                    curr.add_exclude(ex)
            table.append(curr)
    return table

#=== main ===#

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

class SysType (Enum):
    LINUX = 'linux'
    TERMUX = 'termux'
    WINDOWS = 'windows'
if ("termux" in user_home):
    sys_type: SysType = SysType.TERMUX
elif (user_home[0] == "/"):
    sys_type: SysType = SysType.LINUX
else:
    sys_type: SysType = SysType.WINDOWS
import json

print("dot-config: current user home: " + user_home)
print(f"dot-config: your dot-config path is {backup_root}")
print(f"dot-config: your system type is {sys_type}")
print(f"dot-config: dry run mode is {dry_run}")
backup_dirs: list[BackupItem] = load_config()
print(f"Is all the information correct? [y/n] ", end="")
match wait_for_input(wait_for_y_or_n_res):
    case "y":
        print("continuing...")
    case "n":
        print("Exiting")
        exit()
print()

for i in backup_dirs:
    # print(f"((BackupItem i : {i.name}))")
    # print(f"((i.backup_dir : {i.backup_dir}))")
    # print(f"((i.origin_dir : {i.origin_dir}))")
    execute_sync(i)
    print()
