SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
git -C "$SCRIPT_DIR" submodule update --init --recursive
Python3 $SCRIPT_DIR/upload_to_testflight.py