#!/bin/bash
python3 -m venv dasi-venv
source dasi-venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -U nltk
python3 -m pip install -U pyyaml
python3 -m pip install -U chatterbot
python3 -m pip install -U chatterbot_corpus
python3 -m pip install -U spade
python3 -m pip install -U pandas
python3 -m pip install -U sklearn
python3 -m pip install -U googlenews
deactivate
