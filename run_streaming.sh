#!/usr/bin/env bash
# this .sh is to make the streaming run in the background, which will not end even if you close the terminal

chmod +x ./collect_sin_streaming.py

nohup python3 ./collect_sin_streaming.py >/dev/null 2>&1 &

# To see the process's pid, use in terminal:
#   ps ax | grep collect_sin_streaming.py
# to kill it:
#   kill <pid>