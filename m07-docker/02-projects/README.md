******
<details>
<summary>PROJECT 1: Database Containerization and Ephemeral Builds</summary>
<br />
  
#### Project Overview
Demonstrated the configuration of a local development environment by linking a Java application to a containerized MySQL database. Showcased the implementation of dynamic environment variable injection to secure credentials and the execution of an ephemeral Docker container to bypass local dependency issues during the application build phase.

#### Source Code Inspection and Database Deployment
Analyzed the application's source code to identify the specific environment variables required for database connectivity. Subsequently, deployed a standalone MySQL database instance utilizing the official Docker image, mapped the necessary ports, and injected the initialization credentials.
```bash
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# grep -rnw . -e "getenv"
    ./src/main/java/com/example/DatabaseConfig.java:14:    private String user = System.getenv("DB_USER");
    ./src/main/java/com/example/DatabaseConfig.java:15:    private String password = System.getenv("DB_PWD");
    ./src/main/java/com/example/DatabaseConfig.java:16:    private String serverName = System.getenv("DB_SERVER"); // db host name, like localhost without the port
    ./src/main/java/com/example/DatabaseConfig.java:17:    private String dbName = System.getenv("DB_NAME");

    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# docker run \
    > -p 3306:3306 \
    > -e MYSQL_USER=admin \
    > -e MYSQL_PASSWORD=pass \
    > -e MYSQL_DATABASE=project \
    > -e MYSQL_ROOT_PASSWORD=pass \
    > -d mysql
    ...
    Status: Downloaded newer image for mysql:latest
    d63c55a17107b1bacc6e72cc2343f079329843da81e5238415b6f8bc66f60ab8

    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# docker ps
    CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS                                       NAMES
    d63c55a17107   mysql     "docker-entrypoint.s…"   12 seconds ago   Up 11 seconds   0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp   crazy_mahavira
```
#### Ephemeral Application Build Execution
Encountered local build tool mismatches and deprecation issues during the initial compilation attempts. Mitigated the environment mismatch by provisioning an ephemeral Docker container loaded with a modern Gradle engine and JDK 17, successfully compiling the application source code into a deployable JAR artifact.
```bash
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# docker run --rm -v $(pwd):/app -w /app gradle:8.7-jdk17 gradle build
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
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# export DB_USER=admin \
    > export DB_PWD=pass \
    > export DB_SERVER=localhost \
    > export DB_NAME=project

    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# java -jar build/libs/docker-PROJECTs-project-1.0-SNAPSHOT.jar
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
<summary>PROJECT 2: Graphical Database Management Interface Deployment</summary>
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
<summary>PROJECT 3: Multi-Container Orchestration and Data Persistence with Docker Compose</summary>
<br />

#### Project Overview
Demonstrated the orchestration of a multi-tier database environment using Docker Compose. Replaced manual, sequential container deployments with a declarative YAML configuration file. Established service dependencies between a MySQL database and a phpMyAdmin interface, and implemented a named Docker volume to guarantee database data persistence across container lifecycles.

#### Infrastructure as Code Configuration
Authored a `docker-compose.yml` file to define the application stack. Configured port mappings, injected necessary environment variables for authentication, defined inter-container network dependencies (`depends_on`), and mapped a local named volume (`mysql-data`) directly to the MySQL internal data directory (`/var/lib/mysql`).
```bash
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# cat mysqldb.yaml
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
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# docker-compose -f mysqldb.yaml up
    WARN[0000] /mnt/c/Users/emrea/docker-PROJECTs/mysqldb.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
    [+] up 4/4
     ✔ Network docker-PROJECTs_default   Created                                                                                                                                                              0.0s
     ✔ Volume docker-PROJECTs_mysql-data Created                                                                                                                                                              0.0s
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
    local     docker-PROJECTs_mysql-data
    ...

    root@PC:/mnt/c/Users/emrea# docker volume inspect docker-PROJECTs_mysql-data
    [
        {
            "CreatedAt": "2026-04-02T16:16:24Z",
            "Driver": "local",
            "Mountpoint": "/var/lib/docker/volumes/docker-PROJECTs_mysql-data/_data",
            "Name": "docker-PROJECTs_mysql-data",
            "Scope": "local"
        }
    ]

    root@PC:/mnt/c/Users/emrea# docker run -ti --rm -v docker-PROJECTs_mysql-data:/data alpine sh
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
<summary>PROJECT 4: Dockerizing Java Application</summary>
<br />

#### Project Overview
Demonstrated the end-to-end containerization of a compiled Java Spring Boot application. Engineered a lightweight, secure Dockerfile, built the custom image.

#### Dockerfile Configuration and Image Build
Authored a Dockerfile utilizing a minimal `eclipse-temurin:17-jre-alpine` base image to optimize security and footprint. Configured a non-root user (`appuser`) for secure execution and defined the application's entry point. Successfully compiled the configuration into a tagged Docker image (`java-app:1.0`).
```bash
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# cat Dockerfile
    FROM eclipse-temurin:17-jre-alpine

    WORKDIR /home/app

    COPY build/libs/docker-PROJECTs-project-1.0-SNAPSHOT.jar app.jar

    RUN addgroup -S appgroup && adduser -S appuser -G appgroup

    USER appuser

    CMD [ "java", "-jar", "app.jar" ]
    
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# docker build -t java-app:1.0 .
    [+] Building 8.5s (10/10) FINISHED                                                                                                                                                               docker:default
     => [internal] load build definition from Dockerfile                                                                                                                                                       0.1s
     => => transferring dockerfile: 278B                                                                                                                                                                       0.0s
     => [internal] load metadata for docker.io/library/eclipse-temurin:17-jre-alpine                                                                                                                           1.9s
     => [1/4] FROM docker.io/library/eclipse-temurin:17-jre-alpine@sha256:7aa804a1824d18d06c68598fe1c2953b5b203823731be7b9298bb3e0f1920b0d                                                                     4.3s
     => [internal] load build context                                                                                                                                                                          0.6s
     => => transferring context: 27.27MB                                                                                                                                                                       0.6s
     => [2/4] WORKDIR /home/app                                                                                                                                                                                0.1s
     => [3/4] COPY build/libs/docker-PROJECTs-project-1.0-SNAPSHOT.jar app.jar                                                                                                                                0.1s
     => [4/4] RUN addgroup -S appgroup && adduser -S appuser -G appgroup                                                                                                                                       0.4s
     => exporting to image                                                                                                                                                                                     1.4s
     => => naming to docker.io/library/java-app:1.0                                                                                                                                                            0.0s
```

#### Network Integration and Deployment
Resolved connectivity limitations by dynamically injecting database credentials (`-e`) and attaching the container directly to the existing backend network (`--network docker-PROJECTs_default`). The embedded Tomcat server successfully established a database connection and initialized on port 8080.
```bash
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# docker run \
    > -p 8080:8080 \
    > --network docker-PROJECTs_default \
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
<summary>PROJECT 5: Private Docker Registry Integration and Image Publishing</summary>
<br />

#### Overview
Demonstrated the configuration and utilization of a private Docker registry using Sonatype Nexus Repository Manager. Overcame Docker Engine security constraints for HTTP communication, authenticated with the remote server, and successfully published a locally built Java application image to the centralized private repository.

#### Infrastructure Configuration
Provisioned a new Docker hosted repository within the remote Nexus instance, exposing it on port 8083. Modified the local Docker daemon configuration (`daemon.json`) to include the remote server (`167.172.185.199:8083`) in the `insecure-registries` list. This architectural adjustment allowed plain HTTP communication for internal testing, bypassing Docker's default HTTPS requirement.

<img width="1426" height="1125" alt="image" src="https://github.com/user-attachments/assets/1d4aa083-b11d-47cb-818a-39ed64443a0b" />

<img width="1325" height="560" alt="image" src="https://github.com/user-attachments/assets/c892c476-16e5-4606-97f7-394ed780f5dd" />

#### Authentication and Image Preparation
Established an authenticated session with the remote Nexus registry using explicit credentials. Identified the target local image (`java-app:1.0`) and applied a new tag matching the remote registry's DNS/IP and port routing schema. This retagging is a structural prerequisite for the Docker push mechanism to identify the correct destination.
```bash
    root@PC:/mnt/c/Users/emrea# docker login 167.172.185.199:8083
    Username: admin
    Password:
    Login Succeeded

    root@PC:/mnt/c/Users/emrea# docker tag java-app:1.0 167.172.185.199:8083/java-app:1.0

    root@PC:/mnt/c/Users/emrea# docker images | grep java-app
    WARNING: This output is designed for human readability. For machine-readable output, please use --format.
    167.172.185.199:8083/java-app:1.0   681007381347        308MB         92.6MB   U
    java-app:1.0                        681007381347        308MB         92.6MB   U
```
#### Image Publishing
Executed the push operation to transfer the tagged image layers from the local machine directly into the Nexus repository. Validated the upload through the terminal output, confirming the successful transfer of all individual layers and the generation of the final SHA256 digest (`6810073813479e36...`).
```bash
    root@PC:/mnt/c/Users/emrea# docker push 167.172.185.199:8083/java-app:1.0
    The push refers to repository [167.172.185.199:8083/java-app]
    4adb00321f3d: Pushed
    4ebe7a5b83ce: Pushed
    be9a4d7813fc: Pushed
    2b28c8d76488: Pushed
    589002ba0eae: Pushed
    b50a56d2ab38: Pushed
    5e1c552ce83f: Pushed
    8a88a697ab44: Pushed
    b262b9a9131a: Pushed
    1.0: digest: sha256:6810073813479e36333529b8a16fd25eee893a5c19ab517d6079b62a017c7697 size: 856
```
<img width="2000" height="879" alt="image" src="https://github.com/user-attachments/assets/6d1b0759-878c-4486-b9da-62a76f1e2062" />


</details>

******

<details>
<summary>PROJECT 6: Multi-Container Orchestration and Environment Management</summary>
<br />

#### Project Overview
Orchestrated a secure, multi-container architecture consisting of a Java Spring Boot application, a MySQL database, and a phpMyAdmin client using Docker Compose. Engineered the deployment to securely decouple sensitive credentials from the repository by leveraging an external `.env` file. Implemented native service health checks to guarantee strict container initialization sequencing and prevent startup race conditions.

#### Configuration and Environment Management
Authored a `java-app.yaml` Docker Compose manifest defining the service topology, explicit port bindings, and persistent data volumes. Replaced hardcoded credentials with dynamic environment variables (`${VAR}`), ensuring the deployment automatically injects parameters securely sourced from the local `.env` file. 
```bash
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# cat .env
    DB_USER=admin
    DB_PWD=pass
    DB_SERVER=mysql
    DB_NAME=project
    MYSQL_ROOT_PASSWORD=pass
    PMA_HOST=mysql
    PMA_PORT=3306

    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# cat java-app.yaml
    version: '3.8'
    services:
      java-app:
        image: java-app:1.0
        container_name: java-app-composed
        ports:
          - 8080:8080
        environment:
          - DB_USER=${DB_USER}
          - DB_PWD=${DB_PWD}
          - DB_SERVER=${DB_SERVER}
          - DB_NAME=${DB_NAME}
        depends_on:
          mysql:
            condition: service_healthy
      mysql:
        image: mysql
        container_name: mysql
        ports:
          - 3306:3306
        environment:
          - MYSQL_USER=${DB_USER}
          - MYSQL_PASSWORD=${DB_PWD}
          - MYSQL_DATABASE=${DB_NAME}
          - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
        volumes:
          - mysql-data:/var/lib/mysql
        healthcheck:
          test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
          interval: 10s
          timeout: 5s
          retries: 5
      phpmyadmin:
        image: phpmyadmin
        container_name: phpmyadmin
        ports:
          - 8088:80
        environment:
          - PMA_HOST=${PMA_HOST}
          - PMA_PORT=${PMA_PORT}
          - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
        depends_on:
          - mysql
    volumes:
      mysql-data:
        driver: local
```
#### Deployment and Health Check Synchronization
Executed the orchestrated stack deployment. The integration of the `healthcheck` parameter effectively paused the `java-app` container deployment until the internal `mysqladmin ping` command validated the database's readiness. Log outputs confirm the successful establishment of the isolated bridge network, the "Healthy" status resolution of MySQL, and the subsequent synchronized initialization of the Tomcat server and phpMyAdmin client interfaces.
```bash
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# docker-compose -f java-app.yaml up
    WARN[0000] /mnt/c/Users/emrea/docker-PROJECTs/java-app.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
    [+] up 4/4
     ✔ Network docker-PROJECTs_default Created                                                                                                                                                            0.1s
     ✔ Container mysql                  Created                                                                                                                                                            0.1s
     ✔ Container java-app-composed      Created                                                                                                                                                            0.1s
     ✔ Container phpmyadmin             Created                                                                                                                                                            0.2s
    Attaching to java-app-composed, mysql, phpmyadmin
    ...
    mysql       | 2026-04-03T18:40:02.622483Z 1 [System] [MY-013576] [InnoDB] InnoDB initialization has started.
    mysql       | 2026-04-03T18:40:03.276000Z 0 [System] [MY-010931] [Server] /usr/sbin/mysqld: ready for connections. Version: '9.6.0'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server - GPL.
    Container mysql Healthy
    java-app-composed  |
    java-app-composed  |  :: Spring Boot ::                (v3.5.5)
    java-app-composed  |
    java-app-composed  | 2026-04-03T18:40:13.516Z  INFO 1 --- [           main] com.example.Application                  : Starting Application v1.0-SNAPSHOT using Java 17.0.18 with PID 1 (/home/app/app.jar started by appuser in /home/app)
    java-app-composed  | 2026-04-03T18:40:16.874Z  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http) with context path '/'
    java-app-composed  | 2026-04-03T18:40:16.913Z  INFO 1 --- [           main] com.example.Application                  : Started Application in 4.059 seconds (process running for 3.984)
    ...
    phpmyadmin         | 172.19.0.1 - - [03/Apr/2026:18:40:35 +0000] "GET / HTTP/1.1" 200 6060 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# docker ps
    CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS                   PORTS                                         NAMES
    7b0e998ffdd3   phpmyadmin     "/docker-entrypoint.…"   4 minutes ago   Up 3 minutes             0.0.0.0:8088->80/tcp, [::]:8088->80/tcp       phpmyadmin
    5cac775ffba0   java-app:1.0   "/__cacert_entrypoin…"   4 minutes ago   Up 3 minutes             0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp   java-app-composed
    077d192478cd   mysql          "docker-entrypoint.s…"   4 minutes ago   Up 4 minutes (healthy)   0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp   mysql
```


</details>

******

<details>
<summary>PROJECT 7: Remote Server Deployment & Environment Configuration</summary>
<br />


#### Application Reconfiguration & Image Build
Configured the frontend application to point to the remote server's external IP address instead of `localhost`. Recompiled the updated source code, built the new Docker image (`v1.1`), and authenticated with the private Nexus registry to push the artifact securely.
```bash
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# docker build -t 167.172.185.199:8083/java-app:1.1 .
    [+] Building 3.2s (9/9) FINISHED
    ...
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# docker login 167.172.185.199:8083
    Login Succeeded
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# docker push 167.172.185.199:8083/java-app:1.1
    1.1: digest: sha256:2b39a38154f0868680a22b971a005b2ba1b4aa8f6aa7d0aec2563a4c2d906a36 size: 856
```
#### Server Provisioning & Security Configuration
Transferred the necessary deployment manifests (`docker-compose.yaml` and `.env`) to the remote Ubuntu server utilizing secure copy protocol. Adjusted the Docker daemon configuration on the server to allow insecure HTTP connections to the private Nexus repository and restarted the Docker service to apply the registry bypass.
```bash
    root@PC:/mnt/c/Users/emrea/docker-PROJECTs# scp java-app.yaml .env root@167.172.185.199:/root/
    java-app.yaml                                                                 100% 1104    25.0KB/s   00:00
    .env                                                                          100%  112     2.7KB/s   00:00
    ...
    root@ubuntu-docker-nexus:/home/docker-app# echo '{"insecure-registries": ["167.172.185.199:8083"]}' > /var/snap/docker/current/config/daemon.json
    root@ubuntu-docker-nexus:/home/docker-app# snap restart docker
    Restarted.
```
#### Multi-Container Orchestration & Validation
Authenticated the remote server with the private Nexus registry and pulled the updated application image. Deployed the multi-container stack architecture (Java App, MySQL, phpMyAdmin, and Nexus) utilizing an explicit environment variables file (`vars.env`) to ensure secure credential injection while circumventing OS-level hidden file restrictions. Verified successful orchestration, container health states, and proper port bindings.
```bash
    root@ubuntu-docker-nexus:/home/docker-app# docker login 167.172.185.199:8083
    Login Succeeded
    ...
    root@ubuntu-docker-nexus:/home/docker-app# docker pull 167.172.185.199:8083/java-app:1.1
    Status: Downloaded newer image for 167.172.185.199:8083/java-app:1.1
    ...
    root@ubuntu-docker-nexus:/home/docker-app# docker-compose --env-file vars.env -f java-app.yaml up -d
    [+] Running 4/4
     ✔ Network docker-app_default   Created                                                                    0.1s
     ✔ Container mysql              Healthy                                                                   11.2s
     ✔ Container phpmyadmin         Started                                                                    1.0s
     ✔ Container java-app-composed  Started                                                                   11.5s
    
    root@ubuntu-docker-nexus:/home/docker-app# docker ps
    CONTAINER ID   IMAGE                               COMMAND                  CREATED         STATUS                   PORTS                                                                              NAMES
    f99d716ada06   phpmyadmin                          "/docker-entrypoint.…"   3 minutes ago   Up 3 minutes             0.0.0.0:8088->80/tcp, [::]:8088->80/tcp                                            phpmyadmin
    d04384c075e7   167.172.185.199:8083/java-app:1.1   "/__cacert_entrypoin…"   3 minutes ago   Up 3 minutes             0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp                                         java-app-composed
    6584072b48a8   mysql                               "docker-entrypoint.s…"   3 minutes ago   Up 3 minutes (healthy)   0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp, 33060/tcp                              mysql
    7558cf768f95   sonatype/nexus3                     "/opt/sonatype/nexus…"   11 hours ago    Up 35 minutes            0.0.0.0:8081->8081/tcp, [::]:8081->8081/tcp, 0.0.0.0:8083->8083/tcp, [::]:8083->8083/tcp   nexus
```
<img width="855" height="704" alt="image" src="https://github.com/user-attachments/assets/10788d37-1843-4c9e-a603-e738444e1f26" />
<img width="1272" height="638" alt="image" src="https://github.com/user-attachments/assets/1a4ec685-4a96-4072-833a-0de7d4044c5c" />


</details>

******

