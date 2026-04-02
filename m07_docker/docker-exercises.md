******
<details>
<summary>EXERCISE 1: Database Containerization and Ephemeral Builds</summary>
<br />
  
#### Project Overview
Demonstrated the configuration of a local development environment by linking a Java application to a containerized MySQL database. Showcased the implementation of dynamic environment variable injection to secure credentials and the execution of an ephemeral Docker container to bypass local dependency issues during the application build phase.

#### Source Code Inspection and Database Deployment
Analyzed the application's source code to identify the specific environment variables required for database connectivity. Subsequently, deployed a standalone MySQL database instance utilizing the official Docker image, mapped the necessary ports, and injected the initialization credentials.
```bash
    root@PC:/mnt/c/Users/emrea/docker-exercises# grep -rnw . -e "getenv"
    ./src/main/java/com/example/DatabaseConfig.java:14:    private String user = System.getenv("DB_USER");
    ./src/main/java/com/example/DatabaseConfig.java:15:    private String password = System.getenv("DB_PWD");
    ./src/main/java/com/example/DatabaseConfig.java:16:    private String serverName = System.getenv("DB_SERVER"); // db host name, like localhost without the port
    ./src/main/java/com/example/DatabaseConfig.java:17:    private String dbName = System.getenv("DB_NAME");

    root@PC:/mnt/c/Users/emrea/docker-exercises# docker run \
    > -p 3306:3306 \
    > -e MYSQL_USER=admin \
    > -e MYSQL_PASSWORD=pass \
    > -e MYSQL_DATABASE=project \
    > -e MYSQL_ROOT_PASSWORD=pass \
    > -d mysql
    ...
    Status: Downloaded newer image for mysql:latest
    d63c55a17107b1bacc6e72cc2343f079329843da81e5238415b6f8bc66f60ab8

    root@PC:/mnt/c/Users/emrea/docker-exercises# docker ps
    CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS                                       NAMES
    d63c55a17107   mysql     "docker-entrypoint.s…"   12 seconds ago   Up 11 seconds   0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp   crazy_mahavira
```
#### Ephemeral Application Build Execution
Encountered local build tool mismatches and deprecation issues during the initial compilation attempts. Mitigated the environment mismatch by provisioning an ephemeral Docker container loaded with a modern Gradle engine and JDK 17, successfully compiling the application source code into a deployable JAR artifact.
```bash
    root@PC:/mnt/c/Users/emrea/docker-exercises# docker run --rm -v $(pwd):/app -w /app gradle:8.7-jdk17 gradle build
    Unable to find image 'gradle:8.7-jdk17' locally
    ...
    Starting a Gradle Daemon (subsequent builds will be faster)
    > Task :compileJava
    > Task :processResources
    > Task :classes
    ...
    BUILD SUCCESSFUL in 43s
    7 actionable tasks: 7 executed
```
#### Environment Configuration and Application Launch
Configured the host operating system by exporting the targeted database credentials into the shell environment. Launched the compiled Java Spring Boot application, verifying its successful connection to the containerized MySQL database and the initialization of its web servlets to handle browser traffic.
```bash
    root@PC:/mnt/c/Users/emrea/docker-exercises# export DB_USER=admin \
    > export DB_PWD=pass \
    > export DB_SERVER=localhost \
    > export DB_NAME=project

    root@PC:/mnt/c/Users/emrea/docker-exercises# java -jar build/libs/docker-exercises-project-1.0-SNAPSHOT.jar
    ...
    2026-04-02T11:44:20.519+03:00  INFO 1618 --- [           main] com.example.Application                  : Starting Application v1.0-SNAPSHOT using Java 17.0.18...
    2026-04-02T11:44:22.551+03:00  INFO 1618 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port 8080 (http)
    2026-04-02T11:44:23.256+03:00  INFO 1618 --- [           main] com.example.Application                  : Java app started
    2026-04-02T11:44:23.984+03:00  INFO 1618 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http) with context path '/'
    2026-04-02T11:44:24.005+03:00  INFO 1618 --- [           main] com.example.Application                  : Started Application in 4.596 seconds (process running for 5.5)
    2026-04-02T11:44:44.766+03:00  INFO 1618 --- [nio-8080-exec-1] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring DispatcherServlet 'dispatcherServlet'
```

</details>

******

<details>
<summary>EXERCISE 2: Graphical Database Management Interface Deployment</summary>
<br />

#### Project Overview
Demonstrated the deployment of a graphical database administration tool by launching a phpMyAdmin container and linking it to a containerized MySQL database. Showcased inter-container network communication and host port mapping to enable direct browser-based database management.

#### Database and Interface Provisioning
Configured and launched a MySQL database instance with administrative credentials injected via environment variables. Subsequently, provisioned a phpMyAdmin container utilizing the official image. The interface was securely linked to the active MySQL container (`--link mysql:db`) and exposed to the host machine via port 8088 to allow web access.
```bash
    root@PC:/mnt/c/Users/emrea# docker run \
    > -p 3306:3306 \
    > --name mysql \
    > -e MYSQL_USER=admin \
    > -e MYSQL_PASSWORD=pass \
    > -e MYSQL_DATABASE=project \
    > -e MYSQL_ROOT_PASSWORD=pass \
    > -d mysql
    7f686c073ca7cd5e0eaecc4714b718ba61d0c2ff3a9df761c8cc0850c81a792d

    root@PC:/mnt/c/Users/emrea# docker run \
    > -p 8088:80 \
    > --link mysql:db \
    > -d phpmyadmin
    8f1c0bbe664cd69cd0d9347f4137f137c5e7c2841b9ccc7d738cbb7b7daee5f1
```

#### Container Verification and Access Testing
Validated the operational status of both deployed containers. Confirmed that both services were running simultaneously in the background with their respective ports correctly published. Access to the MySQL database was successfully tested by navigating to `localhost:8088` in the browser and authenticating through the phpMyAdmin interface.
```bash
    root@PC:/mnt/c/Users/emrea# docker ps
    CONTAINER ID   IMAGE        COMMAND                  CREATED              STATUS              PORTS                                         NAMES
    8f1c0bbe664c   phpmyadmin   "/docker-entrypoint.…"   3 seconds ago        Up 2 seconds        0.0.0.0:8088->80/tcp, [::]:8088->80/tcp       reverent_johnson
    7f686c073ca7   mysql        "docker-entrypoint.s…"   About a minute ago   Up About a minute   0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp   mysql
```
<img width="1698" height="442" alt="image" src="https://github.com/user-attachments/assets/1125a55f-0d59-4e3a-a061-8b6dd15464bd" />



</details>

******

<details>
<summary>EXERCISE 3: Multi-Container Orchestration and Data Persistence with Docker Compose</summary>
<br />

#### Project Overview
Demonstrated the orchestration of a multi-tier database environment using Docker Compose. Replaced manual, sequential container deployments with a declarative YAML configuration file. Established service dependencies between a MySQL database and a phpMyAdmin interface, and implemented a named Docker volume to guarantee database data persistence across container lifecycles.

#### Infrastructure as Code Configuration
Authored a `docker-compose.yml` file to define the application stack. Configured port mappings, injected necessary environment variables for authentication, defined inter-container network dependencies (`depends_on`), and mapped a local named volume (`mysql-data`) directly to the MySQL internal data directory (`/var/lib/mysql`).
```bash
    root@PC:/mnt/c/Users/emrea/docker-exercises# cat mysqldb.yaml
    version: '3.8'
    services:
      mysql:
        image: mysql
        container_name: mysql
        ports:
          - 3306:3306
        environment:
          - MYSQL_USER=admin
          - MYSQL_PASSWORD=pass
          - MYSQL_DATABASE=project
          - MYSQL_ROOT_PASSWORD=pass
        volumes:
          - mysql-data:/var/lib/mysql

      phpmyadmin:
        image: phpmyadmin
        container_name: phpmyadmin
        ports:
          - 8088:80
        environment:
          - PMA_HOST=mysql
        depends_on:
          - mysql
    volumes:
      mysql-data:
        driver: local
```
#### Automated Stack Deployment
Executed the Compose configuration to automatically provision the isolated network, initialize the persistent volume, and deploy both containers in the correct dependency order.
```bash
    root@PC:/mnt/c/Users/emrea/docker-exercises# docker-compose -f mysqldb.yaml up
    WARN[0000] /mnt/c/Users/emrea/docker-exercises/mysqldb.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
    [+] up 4/4
     ✔ Network docker-exercises_default   Created                                                                                                                                                              0.0s
     ✔ Volume docker-exercises_mysql-data Created                                                                                                                                                              0.0s
     ✔ Container mysql                    Created                                                                                                                                                              0.2s
     ✔ Container phpmyadmin               Created                                                                                                                                                              0.1s
    Attaching to mysql, phpmyadmin
    mysql       | 2026-04-02 16:16:24+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 9.6.0-1.el9 started.
    ...
    mysql       | 2026-04-02T16:16:25.912046Z 1 [System] [MY-013577] [InnoDB] InnoDB initialization has ended.
    mysql       | 2026-04-02 16:16:31+00:00 [Note] [Entrypoint]: Creating database project
    mysql       | 2026-04-02 16:16:31+00:00 [Note] [Entrypoint]: Creating user admin
    mysql       | 2026-04-02 16:16:31+00:00 [Note] [Entrypoint]: Giving user admin access to schema project
    ...
    phpmyadmin  | 172.19.0.1 - - [02/Apr/2026:16:16:35 +0000] "POST /index.php?route=/ HTTP/1.1" 302 1004 "http://localhost:8088/index.php?route=/" 
```
#### Volume Verification and Data Inspection
Conducted rigorous testing to verify data persistence. Inspected the created named volume and utilized an ephemeral Alpine Linux container to mount and view the physical InnoDB data files resting on the host. Cross-referenced these files by directly executing a shell inside the running MySQL container, confirming the volume mapping functioned flawlessly.
```bash
    root@PC:/mnt/c/Users/emrea# docker volume ls
    DRIVER    VOLUME NAME
    local     docker-exercises_mysql-data
    ...

    root@PC:/mnt/c/Users/emrea# docker volume inspect docker-exercises_mysql-data
    [
        {
            "CreatedAt": "2026-04-02T16:16:24Z",
            "Driver": "local",
            "Mountpoint": "/var/lib/docker/volumes/docker-exercises_mysql-data/_data",
            "Name": "docker-exercises_mysql-data",
            "Scope": "local"
        }
    ]

    root@PC:/mnt/c/Users/emrea# docker run -ti --rm -v docker-exercises_mysql-data:/data alpine sh
    / # ls -la /data/
    total 108496
    -rw-r-----    1 999      ping       4194304 Apr  2 16:18 #ib_16384_0.dblwr
    ...
    -rw-r-----    1 999      ping      12582912 Apr  2 16:16 ibdata1
    drwxr-x---    2 999      ping          4096 Apr  2 16:16 mysql
    -rw-r-----    1 999      ping      32505856 Apr  2 16:17 mysql.ibd
    drwxr-x---    2 999      ping          4096 Apr  2 16:16 project
    / # exit

    root@PC:/mnt/c/Users/emrea# docker exec -it 85e7ebde65a0 sh
    sh-5.1# ls -la /var/lib/mysql
    total 108496
    -rw-r----- 1 mysql mysql  4194304 Apr  2 16:18 '#ib_16384_0.dblwr'
    -rw-r----- 1 mysql mysql 12582912 Apr  2 16:16  ibdata1
    drwxr-x--- 2 mysql mysql     4096 Apr  2 16:16  project
    sh-5.1# exit
```

</details>

******

<details>
<summary>EXERCISE 4: Dockerizing Java Application</summary>
<br />

#### Project Overview
Demonstrated the end-to-end containerization of a compiled Java Spring Boot application. Engineered a lightweight, secure Dockerfile, built the custom image.

#### Dockerfile Configuration and Image Build
Authored a Dockerfile utilizing a minimal `eclipse-temurin:17-jre-alpine` base image to optimize security and footprint. Configured a non-root user (`appuser`) for secure execution and defined the application's entry point. Successfully compiled the configuration into a tagged Docker image (`java-app:1.0`).
```bash
    root@PC:/mnt/c/Users/emrea/docker-exercises# cat Dockerfile
    FROM eclipse-temurin:17-jre-alpine

    WORKDIR /home/app

    COPY build/libs/docker-exercises-project-1.0-SNAPSHOT.jar app.jar

    RUN addgroup -S appgroup && adduser -S appuser -G appgroup

    USER appuser

    CMD [ "java", "-jar", "app.jar" ]
    
    root@PC:/mnt/c/Users/emrea/docker-exercises# docker build -t java-app:1.0 .
    [+] Building 8.5s (10/10) FINISHED                                                                                                                                                               docker:default
     => [internal] load build definition from Dockerfile                                                                                                                                                       0.1s
     => => transferring dockerfile: 278B                                                                                                                                                                       0.0s
     => [internal] load metadata for docker.io/library/eclipse-temurin:17-jre-alpine                                                                                                                           1.9s
     => [1/4] FROM docker.io/library/eclipse-temurin:17-jre-alpine@sha256:7aa804a1824d18d06c68598fe1c2953b5b203823731be7b9298bb3e0f1920b0d                                                                     4.3s
     => [internal] load build context                                                                                                                                                                          0.6s
     => => transferring context: 27.27MB                                                                                                                                                                       0.6s
     => [2/4] WORKDIR /home/app                                                                                                                                                                                0.1s
     => [3/4] COPY build/libs/docker-exercises-project-1.0-SNAPSHOT.jar app.jar                                                                                                                                0.1s
     => [4/4] RUN addgroup -S appgroup && adduser -S appuser -G appgroup                                                                                                                                       0.4s
     => exporting to image                                                                                                                                                                                     1.4s
     => => naming to docker.io/library/java-app:1.0                                                                                                                                                            0.0s
```

#### Network Integration and Deployment
Resolved connectivity limitations by dynamically injecting database credentials (`-e`) and attaching the container directly to the existing backend network (`--network docker-exercises_default`). The embedded Tomcat server successfully established a database connection and initialized on port 8080.
```bash
    root@PC:/mnt/c/Users/emrea/docker-exercises# docker run \
    > -p 8080:8080 \
    > --network docker-exercises_default \
    > -e DB_USER=admin \
    > -e DB_PWD=pass \
    > -e DB_SERVER=mysql \
    > -e DB_NAME=project \
    > java-app:1.0

      .   ____          _            __ _ _
     /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
    ( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
     \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
      '  |____| .__|_| |_|_| |_\__, | / / / /
     =========|_|==============|___/=/_/_/_/

     :: Spring Boot ::                (v3.5.5)

    2026-04-02T19:15:01.192Z  INFO 1 --- [           main] com.example.Application                  : Starting Application v1.0-SNAPSHOT using Java 17.0.18 with PID 1 (/home/app/app.jar started by appuser in /home/app)
    2026-04-02T19:15:02.323Z  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port 8080 (http)
    2026-04-02T19:15:02.909Z  INFO 1 --- [           main] com.example.Application                  : Java app started
    2026-04-02T19:15:03.002Z  INFO 1 --- [           main] o.s.b.a.w.s.WelcomePageHandlerMapping    : Adding welcome page: class path resource [static/index.html]
    2026-04-02T19:15:03.324Z  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http) with context path '/'
    2026-04-02T19:15:03.352Z  INFO 1 --- [           main] com.example.Application                  : Started Application in 2.686 seconds (process running for 3.257)
```

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
