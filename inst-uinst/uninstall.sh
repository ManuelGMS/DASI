#!/bin/bash

# begin
echo ""

# tkinter

echo "Would you like to delete tkinter GUI environment of your system? (y/n): "
read -n 1 input

if [ "$input" = "y" ]; then

	sudo apt-get -y install python3-tk

fi

# pip

echo -e "\nWould you like to delete pip package of your system? (y/n): "
read -n 1 input

if [ "$input" = "y" ]; then

	sudo apt-get -y install python3-pip

fi

# venv

echo -e "\nWould you like to delete venv package of your system? (y/n): "
read -n 1 input

if [ "$input" = "y" ]; then

	sudo apt-get -y install python3-venv
	
fi


# end
echo -e "\n"
