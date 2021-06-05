#!/bin/bash
source dasi-venv/bin/activate
export NLTK_DATA=$PWD/nltk_data
python3 main.py
deactivate
