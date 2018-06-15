#!/bin/bash
# rsync script

EXCLUDE='rsync_exclude.txt'
DST_DIR='quest:~/movie_propagation'
SRC_DIR='.'


rsync -rvh --exclude="$EXCLUDE"  "$SRC_DIR" "$DST_DIR"
