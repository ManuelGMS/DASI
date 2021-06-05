#!/bin/bash
source dasi-venv/bin/activate
export NLTK_DATA=$PWD/dasi-env/nltk_data
python3 main.py
deactivate
