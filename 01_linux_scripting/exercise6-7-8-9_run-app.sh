#!/bin/bash
#

NEW_USER=myapp

sudo apt install nodejs npm curl wget net-tools  -y 

echo " NodeJS version: " 
node -v
echo " npm version: "
npm -v 

sudo useradd $NEW_USER -m

sudo runuser -l $NEW_USER -c "curl -o file.tgz https://node-envvars-artifact.s3.eu-west-2.amazonaws.com/bootcamp-node-envvars-project-1.0.0.tgz"
sudo runuser -l $NEW_USER -c "tar -xvzf file.tgz"

read -p " enter the log directory path(like /home/emre/...):" log_dir

if [ -d $log_dir ]
then
	echo " Found existing directory $log_dir "
else
	mkdir -p $log_dir
 	echo " $log_dir directory is created."

fi

fuser -k 3000/tcp

sudo chown $NEW_USER -R $log_dir
sudo runuser -l $NEW_USER -c "

export LOG_DIR=$log_dir
export APP_ENV=dev
export DB_PWD=mysecret
export DB_USER=myuser

cd package

npm install
node server.js &
"
sleep 2 

ps aux | grep node | grep -v grep
netstat -ltnp | grep :3000
