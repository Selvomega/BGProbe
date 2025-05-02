NS_NAME="$1"

# Get the python version number
PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

# Set the PYTHONPATH and PATH
sudo ip netns exec "$NS_NAME" env \
  PATH="~/.local/bin:$PATH" \
  PYTHONPATH="~/.local/lib/python${PYVER}/site-packages" \
  bash
