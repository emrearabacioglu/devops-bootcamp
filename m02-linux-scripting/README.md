# Bash scripting exercises of devops bootcamp 

## EXERCISE 2: Bash Script - Install Java
Write a bash script using Vim editor that installs the latest java version and checks whether java was installed successfully by executing a java -version command.

After installation command, it checks 3 conditions:

1. whether java is installed at all
2. whether an older Java version is installed (java version lower than 11)
3. whether a java version of 11 or higher was installed
It prints relevant informative messages for all 3 conditions. Installation was successful if the 3rd condition is met and you have Java version 11 or higher available.

## EXERCISE 3: Bash Script - User Processes
Write a bash script using Vim editor that checks all the processes running for the current user (USER env var) and prints out the processes in console. Hint: use ps aux command and grep for the user.

## EXERCISE 4: Bash Script - User Processes Sorted
Extend the previous script to ask for a user input for sorting the processes output either by memory or CPU consumption, and print the sorted list.

## EXERCISE 5: Bash Script - Number of User Processes Sorted
Extend the previous script to ask additionally for user input about how many processes to print. Hint: use head program to limit the number of outputs. 

## EXERCISE 6: Bash Script - Start Node App
Write a bash script with following logic: 

Install NodeJS and NPM and print out which versions were installed
Download an artifact file from the URL: https://node-envvars-artifact.s3.eu-west-2.amazonaws.com/bootcamp-node-envvars-project-1.0.0.tgz. Hint: use curl or wget
Unzip the downloaded file
Set the following needed environment variables: APP_ENV=dev, DB_USER=myuser, DB_PWD=mysecret
Change into the unzipped package directory
Run the NodeJS application by executing the following commands:  npm install and node server.js

## EXERCISE 7: Bash Script - Node App Check Status
Extend the script to check after running the application that the application has successfully started and prints out the application's running process and the port where it's listening. 

## EXERCISE 8: Bash Script - Node App with Log Directory
Extend the script to accept a parameter input log_directory: a directory where application will write logs.

The script will check whether the parameter value is a directory name that doesn't exist and will create the directory, if it does exist, it sets the env var LOG_DIR to the directory's absolute path before running the application, so the application can read the LOG_DIR environment variable and write its logs there.

## EXERCISE 9: Bash Script - Node App with Service user
You've been running the application with your user. But we need to adjust that and create own service user: myapp for the application to run. So extend the script to create the user and then run the application with the service user. 
