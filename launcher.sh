#!/bin/bash
#PATH="$HOME/.local/bin:$PATH"
export NLTK_DATA=$PWD/nltk_data
python3 main.py #1> /dev/null 2> /dev/null
