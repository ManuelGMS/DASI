#!/bin/bash

# Librerias del sistema.
sudo apt-get -y install python3-tk
sudo apt-get -y install python3-pip
sudo apt-get -y install python3-venv

# Librerias de python.
pip3 install -U pip
pip3 install -U nltk
pip3 install -U pyyaml
pip3 install -U chatterbot
pip3 install -U chatterbot_corpus
pip3 install -U spade
pip3 install -U pandas
pip3 install -U sklearn
pip3 install -U googlenews
