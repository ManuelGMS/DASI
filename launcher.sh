#!/bin/bash
#source dasi-venv/bin/activate
export NLTK_DATA=$PWD/nltk_data
python3 main.py 1> /dev/null 2> /dev/null
#deactivate
