#!bin/bash

source env/bin/activate
cd bot

# run headless
DISPLAY=":0" python wg-gesucht.py

# run with screen
# python wg-gesucht.py
