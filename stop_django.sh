#!/bin/bash

python3_pid="$(pgrep -o python3)"
ngrok_pid="$(pgrep ngrok)"
kill ${python3_pid}
kill ${ngrok_pid}
