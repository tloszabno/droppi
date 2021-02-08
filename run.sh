#!/bin/bash

cd "$(dirname "$0")"
pipenv run ./droppi.py >> logs.txt 2>&1
