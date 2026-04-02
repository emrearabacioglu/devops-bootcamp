******
<details>
<summary>EXERCISE 1: Start Mysql container</summary>
<br />

First you want to test the application locally with a mysql database. But you don't want to install Mysql, you want to get started fast, so you start it as a docker container:

Start mysql container locally using the official Docker image. Set all needed environment variables.
Export all needed environment variables for your application for connecting with the database (check variable names inside the code)
Build a jar file and start the application. Test access from browser. Make some changes.

</details>

******

<details>
<summary>EXERCISE 2: Start Mysql GUI container</summary>
<br />

Now you have a database, you want to be able to see the database data using a UI tool, so you decide to deploy phpmyadmin. Again, you don't want to install it locally, so you want to start it also as a docker container.

Start phpmyadmin container using the official image.
Access phpmyadmin from your browser and test logging in to your Mysql database

</details>

******

<details>
<summary>EXERCISE 3: Use docker-compose for Mysql and Phpmyadmin</summary>
<br />

You have 2 containers your app needs and you don't want to start them separately all the time. So you configure a docker-compose file for both:

Create a docker-compose file with both containers
Configure a volume for your DB
Test that everything works again

</details>

******

<details>
<summary>EXERCISE 4: Dockerize your Java Application</summary>
<br />

Now you are done with testing the application locally with Mysql database and want to deploy it on the server to make it accessible for others in the team, so they can edit information.

And since your DB and DB UI are running as docker containers, you want to make your app also run as a docker container. So you can all start them using 1 docker-compose file on the server. So you do the following:

Create a Dockerfile for your java application

</details>

******

<details>
<summary>EXERCISE 5: Build and push Java Application Docker Image</summary>
<br />

Now for you to be able to run your java app as a docker image on a remote server, it must be first hosted on a docker repository, so you can fetch it from there on the server. Therefore, you have to do the following:

Create a docker hosted repository on Nexus
Build the image locally and push to this repository

</details>

******

<details>
<summary>EXERCISE 6: Add application to docker-compose</summary>
<br />

Add your application's docker image to docker-compose. Configure all needed env vars.
TIP: Ensure you configure a health check on your mysql container by including the following in your docker-compose file:

```yaml
my-java-app:
  depends_on:
    mysql:
      condition: service_healthy
mysql:
  healthcheck:
    test: [ "CMD", "mysqladmin", "ping", "-h", "localhost" ]
    interval: 10s
    timeout: 5s
    retries: 5
```
Now your app and Mysql containers in your docker-compose are using environment variables.

Make all these environment variable values configurable, by setting them on the server when deploying.
INFO: Again, since docker-compose is part of your application and checked in to the repo, it shouldn't contain any sensitive data. But also allow configuring these values from outside based on an environment

</details>

******

<details>
<summary>EXERCISE 7: Run application on server with docker-compose</summary>
<br />

Finally your docker-compose file is completed and you want to run your application on the server with docker-compose. For that you need to do the following:

Set insecure docker repository on server, because Nexus uses http
Run docker login on the server to be allowed to pull the image
Your application index.html has a hardcoded localhost as a HOST to send requests to the backend. You need to fix that and set the server IP address instead, because the server is going to be the host when you deploy the application on a remote server. (Don't forget to rebuild and push the image and if needed adjust the docker-compose file)
Copy docker-compose.yaml to the server
Set the needed environment variables for all containers in docker-compose
Run docker-compose to start all 3 containers

</details>

******

<details>
<summary>EXERCISE 8: Open ports</summary>
<br />

Congratulations! Your application is running on the server, but you still can't access the application from the browser. You know you need to configure firewall settings. So do the following:

Open the necessary port on the server firewall and
Test access from the browser

</details>

******
