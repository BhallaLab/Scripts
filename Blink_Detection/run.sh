#!/bin/bash

if [ $# -lt 1 ]; then 
    echo "$#"
    echo "USAGE: $1 video_file"
    exit
fi
FILE="$1"
if [ ! -f $FILE ]; then
    echo "$FILE does not exists"
    exit
fi
python ./blinky.py -f $FILE
