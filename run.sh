#!/bin/bash

cd "$(dirname "$0")"
/usr/local/bin/pipenv run python droppi.py >> logs.txt 2>&1
