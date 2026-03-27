#!/bin/bash
#

read -p " Which one would you like to check? CPU or Memory? if you want to see all processes, press enter :  " option


if [[ "$option" == "cpu" || "$option" == "memory" ]]

 then
	echo " $option usage is being listed... "  
       	ps aux | grep emre | grep "$option"
else
	read -p " How many lines of processes would you like to see?:  " lines

	ps aux | grep emre | head -n "$lines"
fi



