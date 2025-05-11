"""
Initialize the const.py and access rights of the repo.
"""

import os
from pathlib import Path

repo_name = "bgp_test"

def get_repo_root() -> str:
    """
    Call in any place inside the repo,
    and return the absolute path of `.../bgp_test/`
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.basename(current_dir) == repo_name:
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break
        current_dir = parent_dir
    raise FileNotFoundError(f"Directory {repo_name} NOT FOUND")

repo_root_path = get_repo_root()
user_name = Path(repo_root_path).parts[2]

const_content = f"""REPO_NAME = \"{repo_name}\"
REPO_ROOT_PATH = \"{repo_root_path}\"
USER_NAME = \"{user_name}\"
"""

with open(f"{repo_root_path}/basic_utils/const.py",'w') as file:
    file.write(const_content)

ROUTING_SOFTWARE_NAME = "frr"
# Let the user to be able to access the repo
os.system(f"sudo setfacl -d -R -m u:{user_name}:rwx {repo_root_path}")
# Let the routing software to be able to access the repo
if ROUTING_SOFTWARE_NAME is not None:
    os.system(f"sudo setfacl -d -R -m u:{ROUTING_SOFTWARE_NAME}:rwx {repo_root_path}")
