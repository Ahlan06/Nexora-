#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [ -f "$DIR/venv/bin/python" ]; then
    exec "$DIR/venv/bin/python" "$DIR/nexora.py"
elif [ -f "$DIR/venv/bin/python3" ]; then
    exec "$DIR/venv/bin/python3" "$DIR/nexora.py"
else
    exec python3 "$DIR/nexora.py"
fi
