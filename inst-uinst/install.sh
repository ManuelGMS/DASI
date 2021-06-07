#!/bin/bash

# Establecemos el PATH para los binarios propios del usuario.
PATH="$PATH:$HOME/.local/bin"

# Instalamos las librerias del sistema.
sudo apt-get -y install python3-tk 1> /dev/null 2> /dev/null
echo "Instalado: 1/11"
sudo apt-get -y install python3-pip 1> /dev/null 2> /dev/null
echo "Instalado: 2/11"

# Actualizamos el instalador pip.
python3 -m pip install -U pip 1> /dev/null 2> /dev/null
echo "Instalado: 3/11"

# Instalamos las librerias de python.
python3 -m pip install nltk 1> /dev/null 2> /dev/null
echo "Instalado: 4/11"
python3 -m pip install spacy 1> /dev/null 2> /dev/null
echo "Instalado: 5/11"
python3 -m pip install chatterbot_corpus 1> /dev/null 2> /dev/null
echo "Instalado: 6/11"
python3 -m pip install spade 1> /dev/null 2> /dev/null
echo "Instalado: 7/11"
python3 -m pip install pandas 1> /dev/null 2> /dev/null
echo "Instalado: 8/11"
python3 -m pip install sklearn 1> /dev/null 2> /dev/null
echo "Instalado: 9/11"
python3 -m pip install googlenews 1> /dev/null 2> /dev/null
echo "Instalado: 10/11"
pip install chatterbot
echo "Instalado: 11/11"