#!/bin/bash

# Librerias del sistema.
sudo apt-get -y install python3-tk
sudo apt-get -y install python3-pip

# Librerias de python.
python3 -m pip install -U pip
python3 -m pip install -U nltk
python3 -m pip install -U chatterbot
python3 -m pip install -U chatterbot_corpus
python3 -m pip install -U spade
python3 -m pip install -U pandas
python3 -m pip install -U sklearn
python3 -m pip install -U googlenews
