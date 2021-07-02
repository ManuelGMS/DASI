#!/bin/bash

# Establecemos el PATH para los binarios propios del usuario.
PATH="$PATH:$HOME/.local/bin"

# Instalamos las librerias del sistema.
echo "Instalando: python3-tk"
sudo apt-get -y install python3-tk 1> /dev/null 2> /dev/null
echo "Se ha Instalado: python3-tk"
echo "Instalando: python3-pip"
sudo apt-get -y install python3-pip 1> /dev/null 2> /dev/null
echo "Se ha Instalado: python3-pip"

# Actualizamos el instalador pip.
echo "Actualizando: pip"
python3 -m pip install -U pip 1> /dev/null 2> /dev/null
echo "Se ha actualizado: pip"

# Instalamos las librerias de python.
echo "Instalando: nltk"
python3 -m pip install nltk 1> /dev/null 2> /dev/null
echo "Se ha Instalado: nltk"
echo "Instalando: spacy"
python3 -m pip install spacy 1> /dev/null 2> /dev/null
echo "Se ha Instalado: spacy"
echo "Instalando: chatterbot_corpus"
python3 -m pip install chatterbot_corpus 1> /dev/null 2> /dev/null
echo "Se ha Instalado: chatterbot_corpus"
echo "Instalando: spade"
python3 -m pip install spade 1> /dev/null 2> /dev/null
echo "Se ha Instalado: spade"
echo "Instalando: pandas"
python3 -m pip install pandas 1> /dev/null 2> /dev/null
echo "Se ha Instalado: pandas"
echo "Instalando: sklearn"
python3 -m pip install sklearn 1> /dev/null 2> /dev/null
echo "Se ha Instalado: sklearn"
echo "Instalando: googlenews"
python3 -m pip install googlenews 1> /dev/null 2> /dev/null
echo "Se ha Instalado: googlenews"
echo "Instalando: chatterbot"
python3 -m pip install chatterbot 1> /dev/null 2> /dev/null
echo "Se ha Instalado: chatterbot"