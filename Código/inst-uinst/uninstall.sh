#!/bin/bash

# begin
echo ""

# tkinter

echo "Would you like to delete tkinter GUI environment of your system? (y/n): "
read -n 1 input

if [ "$input" = "y" ]; then

	echo ""
	sudo apt-get -y purge python3-tk 1> /dev/null 2> /dev/null
	echo "Package removed."

fi

# pip3

echo -e "\nWould you like to delete pip package of your system? (y/n): "
read -n 1 input

if [ "$input" = "y" ]; then

	echo ""
	sudo apt-get -y purge python3-pip 1> /dev/null 2> /dev/null
	echo "Package removed."

fi

# end
echo -e "\n"
