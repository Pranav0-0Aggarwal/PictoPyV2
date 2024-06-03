#!/bin/sh

rm .images/output/*

sleep 2

fastfetch

sleep 4

echo "
============

Size of dataset

============
"
echo "$ du -sh .images"
du -sh .images

sleep 4

echo "
============
$ time python main.py
"
echo "
Scanning the whole Drive ...
"
source .venv/bin/activate
time python main.py

sleep 4

echo "
============
DB schema:
============
"
sqlite3 ~/.pictopy.db .schema

sleep 4

echo "
=========
Image output here is only for testing porpose, won't be created in production, thus saving time
========="