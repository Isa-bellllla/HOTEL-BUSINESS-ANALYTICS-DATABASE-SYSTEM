#!/bin/sh
set -eu

HOTEL_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
for HOTEL_PYTHON in /usr/local/bin/python3 /opt/homebrew/bin/python3 /Library/Frameworks/Python.framework/Versions/Current/bin/python3 "$(command -v python3 || true)" /opt/anaconda3/bin/python; do
    if [ -x "$HOTEL_PYTHON" ] && "$HOTEL_PYTHON" -I -B -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
        exec "$HOTEL_PYTHON" -I -B "$HOTEL_DIR/launch_hotel.py" "$@"
    fi
done
printf '%s\n' '需要 Python 3.10 或更新版本。请安装 Python 后再次双击。' >&2
exit 1
