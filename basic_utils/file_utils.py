from .const import USER_NAME
import os

TESTCASE_DUMP_SINGLE = 'log/test_single'
TESTCASE_DUMP_BATCHED = 'log/test_batched'
TESTCASE_DUMP_CRASHED = 'log/test_crashed'

def directory_exists(dir_path: str) -> bool:
    """Check if the directory exists."""
    return os.path.exists(dir_path) and os.path.isdir(dir_path)

def file_exists(file_path: str) -> bool:
    """Check if the file exists."""
    return os.path.exists(file_path) and os.path.isfile(file_path)

def create_dir(dir_path: str):
    """Create a directory."""
    os.mkdir(dir_path)

def create_file(file_path: str, content: str):
    """Create a file with given content."""
    with open(file_path, 'w') as file:
        file.write(content)

def allow_user_access(path: str):
    """
    Give user access to given path.
    """
    os.system(f"sudo setfacl -d -R -m u:{USER_NAME}:rwx {path}")
