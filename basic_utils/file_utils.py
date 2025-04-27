import os

REPO_NAME = 'bgp_test'
TESTCASE_DUMP_SINGLE = 'test_records_single'
TESTCASE_DUMP_BATCHED = 'test_records_batched'
TESTCASE_DUMP_CRASHED = 'test_records_crashed'

def get_repo_root() -> str:
    """
    Call in any place inside the repo,
    and return the absolute path of `.../bgp_test/`
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.basename(current_dir) == REPO_NAME:
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break
        current_dir = parent_dir
    raise FileNotFoundError(f"Directory {REPO_NAME} NOT FOUND")

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
