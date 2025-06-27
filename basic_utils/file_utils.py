from .const import USER_NAME
import os

TESTCASE_DUMP_SINGLE = 'data/test_single'
TESTCASE_DUMP_BATCHED = 'data/test_batched'
TESTCASE_DUMP_CRASHED = 'data/test_crashed'
TESTCASE_DUMP_REPEATED = 'data/test_repeated'
TESTCASE_DUMP_PLAYGROUND = 'data/test_playground'

def directory_exists(dir_path: str) -> bool:
    """Check if the directory exists."""
    return os.path.exists(dir_path) and os.path.isdir(dir_path)

def file_exists(file_path: str) -> bool:
    """Check if the file exists."""
    return os.path.exists(file_path) and os.path.isfile(file_path)

def create_dir(dir_path: str):
    """Create a directory."""
    if not directory_exists(dir_path):
        os.mkdir(dir_path)

def create_file(file_path: str, content: str):
    """Create a file with given content."""
    with open(file_path, 'w') as file:
        file.write(content)

def delete_file(file_path: str):
    """Delete the given file."""
    if file_exists(file_path):
        os.system(f"sudo rm {file_path}")

def list_subdirectories(path: str):
    """List all subdirectories under the input directory."""
    return [name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name))]

def allow_user_access(path: str):
    """
    Give user access to given path.
    """
    os.system(f"sudo setfacl -R -m u:{USER_NAME}:rwx {path}")
    os.system(f"sudo setfacl -d -R -m u:{USER_NAME}:rwx {path}")
