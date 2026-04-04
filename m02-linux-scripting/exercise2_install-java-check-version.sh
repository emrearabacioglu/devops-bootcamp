#!/bin/bash

sudo apt install -y default-jre

java_ver=$(java -version 2>&1 |grep version | awk '{print $3}' | tr -d '"' | awk -F '.' '{print $1}')

if [ "$java_ver" == "" ]
 then
	echo " Java was nt found "
elif [ "$java_ver" -lt 11 ]
 then
	echo " Java was installed but its an old version: $java_ver "

elif [ "$java_ver" -ge 11 ]
 then
	 echo " New java version installed succesfully: $java_ver "

fi


