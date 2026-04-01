# Containers with Docker

******

<details>
<summary>Main Docker Commands</summary>
 <br />

#### Installed Docker on local machine

Demo executed - run two different Versions of Postgres Docker Images:

```bash

docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword postgres:13.10

docker run --name some-postgres-new -e POSTGRES_PASSWORD=mysecretpassword -d postgres:14.7

PS C:\Users\emrea> docker ps
CONTAINER ID   IMAGE            COMMAND                  CREATED          STATUS          PORTS      NAMES
c7056dad1904   postgres:14.7    "docker-entrypoint.s…"   4 seconds ago    Up 3 seconds    5432/tcp   some-postgres-new
ede91111c847   postgres:13.10   "docker-entrypoint.s…"   11 minutes ago   Up 11 minutes   5432/tcp   some-postgres

```
 
#### Image Management
Demonstrated fetching the latest Redis image and verifying local image storage.

```bash
PS C:\Users\emrea> docker pull redis
Using default tag: latest
latest: Pulling from library/redis
...
Status: Downloaded newer image for redis:latest

PS C:\Users\emrea> docker images
IMAGE             ID             DISK USAGE   CONTENT SIZE
postgres:14.7     5ac16ee31134        541MB          138MB
redis:latest      009cc37796fb        204MB         55.3MB
```
#### Container Lifecycle
Executed containers in detached mode and managed start/stop state transitions.
```bash
PS C:\Users\emrea> docker run -d redis
16cddd06392f2f1b554911b51b2c2b6e2acd6c6844fc3c98edadc696e16d6a83

PS C:\Users\emrea> docker stop 16cddd06392f
16cddd06392f

PS C:\Users\emrea> docker ps -a
CONTAINER ID   IMAGE   COMMAND                  CREATED         STATUS                      NAMES
16cddd06392f   redis   "docker-entrypoint.s…"   2 minutes ago   Exited (0) 23 seconds ago   gracious_cohen
```

#### Port Binding & Conflict Resolution
Configured host-to-container port mapping and resolved an allocation conflict by deploying a secondary database version on an alternate port.

```bash
PS C:\Users\emrea> docker run -p 6000:6379 -d redis
f71b5d49234c017891ce9870d82cba2eee9bc1be0ab7b80e6e4be466efa9530d

PS C:\Users\emrea> docker run -p 6000:6379 -d redis:6.2
docker: Error response from daemon: failed to set up container networking... Bind for 0.0.0.0:6000 failed: port is already allocated

PS C:\Users\emrea> docker run -p 6001:6379 -d redis:6.2
37ce9f8db5c64f4ecf96a84bae62e3f46e833a2f25832c619f9d1846053fc19a

PS C:\Users\emrea> docker ps
CONTAINER ID   IMAGE       STATUS              PORTS                                         NAMES
37ce9f8db5c6   redis:6.2   Up 7 seconds        0.0.0.0:6001->6379/tcp, [::]:6001->6379/tcp   gifted_tu
f71b5d49234c   redis       Up About a minute   0.0.0.0:6000->6379/tcp, [::]:6000->6379/tcp   intelligent_swartz
```

#### Docker Command Referance

* `docker pull`: Fetch images from the registry.
* `docker images`: Audit local images and disk usage.
* `docker run`: Execute a container in the foreground.
* `docker run -d`: Deploy a container in detached mode.
* `docker stop`: Halt an active container.
* `docker start`: Restart an exiting container.
* `docker ps`: Monitor active containers and ports.
* `docker ps -a`: List lifecycle history of all containers.
* `docker run -p`: Configure host-to-container port binding.


### Debug Commands:


#### Log Analysis
Audited container startup sequences and background logs using both IDs and assigned names.

```bash
PS C:\Users\emrea> docker logs redis-latest
Starting Redis Server
1:C 30 Mar 2026 08:08:05.297 * oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
...
1:M 30 Mar 2026 08:08:05.309 * Server initialized
1:M 30 Mar 2026 08:08:05.309 * Ready to accept connections tcp
```

#### Conflict Resolution
Cleared container naming conflicts by removing the overlapping instance and redeploying the service.

```bash
PS C:\Users\emrea> docker run -p 6000:6379 --name redis-latest -d redis
docker: Error response from daemon: Conflict. The container name "/redis-latest" is already in use...

PS C:\Users\emrea> docker rm 39c1098584d283a2cbe5fa018437be5f91c3efe4f8daba91adff6e0423ec6bb7
39c1098584d283a2cbe5fa018437be5f91c3efe4f8daba91adff6e0423ec6bb7

PS C:\Users\emrea> docker run -p 6000:6379 --name redis-latest -d redis
51015e2ff703884920419380a3fdaf86ea7a2756aedde49b513d763d510718d5
```

#### Interactive Shell (Exec)
Accessed the internal bash shell to inspect file systems and environment variables.

```bash
PS C:\Users\emrea> docker exec -it 51015e2ff703 /bin/bash
root@51015e2ff703:/data# cd /
root@51015e2ff703:/# env
HOSTNAME=51015e2ff703
PWD=/
HOME=/root
TERM=xterm
SHLVL=1
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
_=/usr/bin/env
OLDPWD=/data
root@51015e2ff703:/# exit
exit

PS C:\Users\emrea> docker exec -it redis-older /bin/bash
root@26cb48b6efb7:/data# exit

```
#### Docker Debugging Command Reference

* `docker ps`: Monitor active containers and verified port mappings.
* `docker logs`: Retriev background execution and initialization logs.
* `docker stop`: Halt specific running containers.
* `docker run`: Deploy named containers in detached mode with specific port configurations.
* `docker rm`: Delete specific containers to resolve naming conflicts.
* `docker exec`: Establish an interactive bash shell session inside a running container for inspection.

</details>


******

## Docker Demo Projects


<details>
<summary>Developing with Docker</summary>
 <br />

#### Project Overview
Demonstrated the orchestration of a multi-container environment utilizing Docker. Successfully provisioned a MongoDB database and a Mongo Express administrative interface within an isolated custom network, and integrated them with a local Node.js backend application.

#### Image Acquisition
Fetched the required official database and management UI images from the Docker registry.

```bash
    root@PC:/mnt/c/Users/emrea# docker pull mongo
    Using default tag: latest
    latest: Pulling from library/mongo
    0c85015575ad: Pull complete
    ...
    Status: Downloaded newer image for mongo:latest
    docker.io/library/mongo:latest

    root@PC:/mnt/c/Users/emrea# docker pull mongo-express
    Using default tag: latest
    latest: Pulling from library/mongo-express
    0bf3571b6cd7: Pull complete
    ...
    Status: Downloaded newer image for mongo-express:latest
    docker.io/library/mongo-express:latest
```
#### Network Configuration
Configured a dedicated Docker bridge network to ensure secure inter-container DNS resolution and traffic routing.
```bash
    root@PC:/mnt/c/Users/emrea# docker network create mongo-network
    16e494395ea4e77528ff206d9c2358b3e0e05095d8cd1bff5deffc15ec85439f
```
#### Database Provisioning
Deployed the MongoDB container in detached mode, attaching it to the custom network with root authentication variables injected.
```bash
    root@PC:/mnt/c/Users/emrea/js-app# docker run -d \
    > -p 27017:27017 \
    > -e MONGO_INITDB_ROOT_USERNAME=admin
    > -e MONGO_INITDB_ROOT_PASSWORD=password \
    > --name mongodb \
    > --network mongo-network \
    > mongo
    d06a3779f6f07ce42d3ae0e63a3826108167bc0cefc1e403dffe4849aad747cd
```
#### Management Interface Deployment
Launched the Mongo Express container, passing database credentials and server routing parameters to establish a connection with the active MongoDB instance.
```bash
    root@PC:/mnt/c/Users/emrea/js-app# docker run -d \
    > -p 8081:8081 \
    > -e ME_CONFIG_MONGODB_ADMINUSERNAME=admin \
    > -e ME_CONFIG_MONGODB_ADMINPASSWORD=password \
    > -e ME_CONFIG_BASICAUTH_USERNAME=user \
    > -e ME_CONFIG_BASICAUTH_PASSWORD=pass \
    > --network mongo-network \
    > --name mongo-express \
    > -e ME_CONFIG_MONGODB_SERVER=mongodb \
    > -e ME_CONFIG_MONGODB_URL=mongodb://mongodb:27017 \
    > mongo-express
    abfc2ece56bd7cfb551269a1b635e1a5504feb788b71c00cba972e15867483ca
```
#### Infrastructure Validation
Verified the execution state and port bindings of the active container instances.
```bash
    root@PC:/mnt/c/Users/emrea/js-app# docker ps
    CONTAINER ID   IMAGE           COMMAND                  CREATED          STATUS          PORTS                                             NAMES
    abfc2ece56bd   mongo-express   "/sbin/tini -- /dock…"   10 minutes ago   Up 10 minutes   0.0.0.0:8081->8081/tcp, [::]:8081->8081/tcp       mongo-express
    d06a3779f6f0   mongo           "docker-entrypoint.s…"   20 minutes ago   Up 20 minutes   0.0.0.0:27017->27017/tcp, [::]:27017->27017/tcp   mongodb
```
#### Application Integration
Executed the Node.js application, successfully confirming the backend's ability to communicate with the containerized database architecture.
```bash
    root@PC:/mnt/c/Users/emrea/js-app# node app/server.js &
    [2] 8313
    root@PC:/mnt/c/Users/emrea/js-app# app listening on port 3000!
 ```

#### Real-Time Log Monitoring & Verification
Tailed the active database container logs to observe live events. Verified successful data manipulation triggered via the application interface (e.g., dynamic creation of new collections), confirming complete end-to-end integration.
```bash
    root@PC:/mnt/c/Users/emrea/js-app# docker logs d06a3779f6f0 -f
    ...
    {"t":{"$date":"2026-03-30T14:44:26.370+00:00"},"s":"I",  "c":"STORAGE",  "id":20320,   "ctx":"conn3","msg":"createCollection","attr":{"namespace":"user-account.delete_me","uuidDisposition":"generated","uuid":{"uuid":{"$uuid":"455e0feb-27c9-41ad-99f0-af106ab9e20a"}},"options":{}}}
    {"t":{"$date":"2026-03-30T14:44:26.388+00:00"},"s":"I",  "c":"INDEX",    "id":20345,   "ctx":"conn3","msg":"Index build: done building","attr":{"buildUUID":null,"collectionUUID":{"uuid":{"$uuid":"455e0feb-27c9-41ad-99f0-af106ab9e20a"}},"namespace":"user-account.delete_me","index":"_id_","ident":"index-44762920-9339-4602-8461-65420390af58","collectionIdent":"collection-e0b598e2-51d3-445e-82ab-19c24c309036","commitTimestamp":null}}
    ...
    {"t":{"$date":"2026-03-30T14:47:52.502+00:00"},"s":"I",  "c":"STORAGE",  "id":20320,   "ctx":"conn3","msg":"createCollection","attr":{"namespace":"user-account.users","uuidDisposition":"generated","uuid":{"uuid":{"$uuid":"df633f76-4d26-4c7f-a825-b94a6bea7912"}},"options":{}}}
```
    
</details>

******

<details>
<summary>Docker Compose - Run multiple Docker containers</summary>
 <br />

### Demo Project: Multi-Container Orchestration with Docker Compose

#### Project Overview
Demonstrated the transition from imperative container management to a declarative orchestration approach using Docker Compose. Engineered a `mongo.yaml` configuration to provision a MongoDB database and a Mongo Express administrative interface. Successfully deployed the stack, verified internal network isolation, integrated a local Node.js backend, and managed the complete teardown lifecycle.

#### Infrastructure Configuration
Defined the multi-container architecture, specifying target images, port bindings, and authentication credentials within a declarative YAML format.

```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# cat mongo.yaml
    version: '3'
    services:
      mongodb:
        image: mongo
        ports:
          - 27017:27017
        environment:
          - MONGO_INITDB_ROOT_USERNAME=admin
          - MONGO_INITDB_ROOT_PASSWORD=password
      mongo-express:
        image: mongo-express
        ports:
          - 8081:8081
        restart: always
        environment:
          - ME_CONFIG_MONGODB_ADMINUSERNAME=admin
          - ME_CONFIG_MONGODB_ADMINPASSWORD=password
          - ME_CONFIG_BASICAUTH_USERNAME=user
          - ME_CONFIG_BASICAUTH_PASSWORD=pass
          - ME_CONFIG_MONGODB_SERVER=mongodb
          - ME_CONFIG_MONGODB_URL=mongodb://mongodb:27017
```

#### Stack Deployment
Deployed the infrastructure using Docker Compose. Verified the automatic provisioning of the isolated `app_default` network and the initialization of both database and UI containers.

```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# docker-compose -f mongo.yaml up
    WARN[0000] /mnt/c/Users/emrea/js-app/app/mongo.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
    [+] up 3/3
     ✔ Network app_default           Created                                                                                                                                                             0.0s
     ✔ Container app-mongo-express-1 Created                                                                                                                                                             0.2s
     ✔ Container app-mongodb-1       Created                                                                                                                                                             0.1s
    Attaching to mongo-express-1, mongodb-1
    mongo-express-1  | Waiting for mongodb:27017...
    mongodb-1        | {"t":{"$date":"2026-03-30T17:31:07.876+00:00"},"s":"I",  "c":"-",        "id":8991200, "ctx":"main","msg":"Shuffling initializers","attr":{"seed":845250285}}
    ...
    mongo-express-1  | Mongo Express server listening at http://0.0.0.0:8081
    mongo-express-1  | Server is open to allow connections from anyone (0.0.0.0)
```

#### Infrastructure Verification & Application Integration
Validated the active stack via a secondary terminal session. Confirmed network creation and successfully executed the Node.js application to interact with the compose-managed database.
```bash
    root@PC:/mnt/c/Users/emrea# docker network ls
    NETWORK ID     NAME            DRIVER    SCOPE
    fa6033aaed99   app_default     bridge    local
    47950cfb6fd3   bridge          bridge    local
    ...
    
    root@PC:/mnt/c/Users/emrea# docker ps
    CONTAINER ID   IMAGE           COMMAND                  CREATED          STATUS          PORTS                                             NAMES
    37435ab2639d   mongo           "docker-entrypoint.s…"   3 minutes ago    Up 3 minutes    0.0.0.0:27017->27017/tcp, [::]:27017->27017/tcp   app-mongodb-1
    4f73371e9d40   mongo-express   "/sbin/tini -- /dock…"   3 minutes ago    Up 3 minutes    0.0.0.0:8081->8081/tcp, [::]:8081->8081/tcp       app-mongo-express-1
    
    root@PC:/mnt/c/Users/emrea/js-app/app# node server.js
    app listening on port 3000!
```
    

#### Teardown and Cleanup
Demonstrated a teardown of the environment. Successfully removed all associated containers and custom networks allocated by the compose configuration.
```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# docker-compose -f mongo.yaml down
    WARN[0000] /mnt/c/Users/emrea/js-app/app/mongo.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
    [+] down 3/3
     ✔ Container app-mongo-express-1 Removed                                                                                                                                                             0.4s
     ✔ Container app-mongodb-1       Removed                                                                                                                                                             0.5s
     ✔ Network app_default           Removed                                                                                                                                                             0.3s
```
     
### Verify the function
Checked the UI to see whether the changes made in the APP reflected to in the database:

<img width="2554" height="942" alt="image" src="https://github.com/user-attachments/assets/0e450953-b119-408e-b1bb-ff013cf50b80" />


#### Command Summary

* `docker-compose -f [file] up`: Parses the specified YAML file to build, (re)create, and start the entire service stack.
* `docker-compose -f [file] down`: Safely stops and removes containers, networks, and associated resources created by the `up` command.
  
</details>

******

<details>
<summary>Dockerfile - Build your own Docker Image</summary>
 <br />

### Demo Project: Containerizing a Node.js Application

#### Project Overview
Demonstrated the end-to-end process of containerizing a custom Node.js application. Engineered a `Dockerfile`, managed the image build process with version tagging, and orchestrated the underlying database infrastructure utilizing Docker Compose. Verified the final deployment through interactive internal container debugging.

#### Infrastructure Orchestration
Configured and deployed a multi-container database stack (MongoDB and Mongo Express) using a declarative Docker Compose workflow to support the application backend.

```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# docker-compose -f mongo.yaml up
    WARN[0000] /mnt/c/Users/emrea/js-app/app/mongo.yaml: the attribute `version` is obsolete...
    [+] up 3/3
     ✔ Network app_default           Created                                                                                                                                                             0.0s
     ✔ Container app-mongo-express-1 Created                                                                                                                                                             0.2s
     ✔ Container app-mongodb-1       Created                                                                                                                                                             0.1s
```

#### Application Containerization (Dockerfile)
Developed a `Dockerfile` utilizing the lightweight `node:20-alpine` base image. Injected necessary environment variables, established secure working directories, mapped the source code, and managed node dependencies dynamically.
```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# cat Dockerfile
    FROM node:20-alpine

    ENV MONGO_DB_USERNAME=admin \
        MONGO_DB_PWD=password

    RUN mkdir -p /home/app

    COPY ./app /home/app

    WORKDIR /home/app

    RUN npm install

    CMD ["node", "server.js"]
```
#### Image Construction and Iteration
Built the custom Docker image and tagged it for version control (`my-app:1.0`). Successfully troubleshot and resolved initial pathing conflicts by restructuring the local build context and modifying the `WORKDIR` before finalizing the build.
```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# docker build -t my-app:1.0 .
    [+] Building 14.8s (11/11) FINISHED                                                               docker:default
     => [internal] load build definition from Dockerfile                                                        0.0s
     => => transferring dockerfile: 225B                                                                        0.0s
     => [internal] load metadata for docker.io/library/node:20-alpine                                           1.0s
     => [internal] load build context                                                                           0.3s
     => => transferring context: 6.08MB                                                                         0.3s
     => [3/5] COPY ./app /home/app                                                                              0.1s
     => [4/5] WORKDIR /home/app                                                                                 0.0s
     => [5/5] RUN npm install                                                                                   9.9s
     => exporting to image                                                                                      3.4s
     => => naming to docker.io/library/my-app:1.0                                                               0.0s
```
#### Deployment and Internal Validation
Deployed the constructed application image in detached mode. Accessed the isolated container environment interactively via a shell to validate the directory structure, dependencies, and runtime variables.
```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# docker run -d my-app:1.0
    059e8cd35881d2b85b3f5219df7cb094759705fa69c055e86d5552fedc0c5344

    root@PC:/mnt/c/Users/emrea# docker exec -it 059e8cd35881 /bin/sh
    /home/app # ls
    images             index.html         node_modules       package-lock.json  package.json       server.js
```
    
#### Command Summary

* `docker build -t [name:tag] .`: Constructs a Docker image from a local `Dockerfile` and assigns it a specific version tag.
* `docker rmi [image]`: Removes a specific Docker image from the local registry to free up space.
* `docker rm [container_id]`: Deletes a stopped or exited container.
* `docker exec -it [container_id] /bin/sh`: Opens an interactive shell session inside a running container for direct debugging and exploration.
 
</details>

******

<details>
<summary>Private Docker Repository</summary>
 <br />

### Demo Project: Integrating Docker with Nexus Repository Manager

#### Project Overview

Demonstrated the configuration and integration of Sonatype Nexus as a private Docker registry. Provisioned a Docker-hosted repository, established Role-Based Access Control (RBAC), and configured droplet firewalls. Successfully authenticated the local Docker CLI with the remote Nexus server, tagged a local application image, and securely pushed the artifact to the private registry. Verified the deployment state via the Nexus REST API.

#### Infrastructure & Access Configuration
Configured a new Docker Hosted repository on Nexus with a dedicated repository connector on port 8083. Established specific user roles for secure access. Modified the droplet's firewall rules to expose port 8083 and enabled the "Docker Bearer Token Realm" in Nexus for authentication. Configured the local Docker Desktop engine to accept the Nexus IP and port as an insecure registry.

<img width="1584" height="1075" alt="image" src="https://github.com/user-attachments/assets/de4fb996-b582-4d2b-840c-6e9761c73d5c" />

<img width="1668" height="683" alt="image" src="https://github.com/user-attachments/assets/f1c82796-1769-492d-8704-12c095f3bb4a" />



#### Registry Authentication
Authenticated the local Docker CLI with the remote Nexus repository using the configured repository credentials.
```bash
    root@PC:/mnt/c/Users/emrea# docker login 46.101.180.141:8083
    Username: emre
    Password:
    Error response from daemon: login attempt to http://46.101.180.141:8083/v2/ failed with status: 401 Unauthorized
    root@PC:/mnt/c/Users/emrea# docker login 46.101.180.141:8083
    Username: emre
    Password:
    Login Succeeded
```
#### Artifact Preparation
Identified the target local Node.js application image (`my-app:1.0`) and tagged it to align with the remote Nexus repository's routing structure.
```bash
    root@PC:/mnt/c/Users/emrea# docker images
                                                                                                                     i Info →   U  In Use
    IMAGE                  ID             DISK USAGE   CONTENT SIZE   EXTRA
    ...
    my-app:1.0             e18236b5d15e        325MB         70.2MB   U
    ...
    root@PC:/mnt/c/Users/emrea# docker tag my-app:1.0 46.101.180.141:8083/my-app:1.0
    root@PC:/mnt/c/Users/emrea# docker images | grep my-app
    WARNING: This output is designed for human readability. For machine-readable output, please use --format.
    46.101.180.141:8083/my-app:1.0   e18236b5d15e        325MB         70.2MB   U
    my-app:1.0                       e18236b5d15e        325MB         70.2MB   U
```
#### Artifact Deployment
Executed the push command to upload the tagged Docker image to the Nexus private repository.
```bash
    root@PC:/mnt/c/Users/emrea# docker push 46.101.180.141:8083/my-app:1.0
    The push refers to repository [46.101.180.141:8083/my-app]
    0833ce1427bb: Pushed
    589002ba0eae: Pushed
    43867c4bf195: Pushed
    d7f6aca05b78: Pushed
    4f4fb700ef54: Pushed
    6997feec4bf3: Pushed
    62e0e1181d88: Pushed
    1fc98b148f65: Pushed
    c7734204880f: Pushed
    1.0: digest: sha256:e18236b5d15efc36509934d76863dc051371070b1b852dac07dec857822c596e size: 856
```
#### Deployment Verification via API
Verified the successful artifact upload by querying the Nexus REST API directly from the terminal, confirming the presence and metadata of the pushed Docker image.
```bash
    root@PC:/mnt/c/Users/emrea# curl -u emre:12345678 -X GET '46.101.180.141:8081/service/rest/v1/components?repository=docker-hosted'
    {
      "items" : [ {
        "id" : "ZG9ja2VyLWhvc3RlZDo0ZjFiYmNkZA",
        "repository" : "docker-hosted",
        "format" : "docker",
        "group" : "",
        "name" : "my-app",
        "version" : "1.0",
        "assets" : [ {
          "downloadUrl" : "http://46.101.180.141:8081/repository/docker-hosted/v2/my-app/manifests/1.0",
          "path" : "/v2/my-app/manifests/1.0",
          "id" : "ZG9ja2VyLWhvc3RlZDphMmEwMTBmMw",
          "repository" : "docker-hosted",
          "format" : "docker",
          "checksum" : {
            "sha256" : "e18236b5d15efc36509934d76863dc051371070b1b852dac07dec857822c596e",
            "sha1" : "ee76f1c7bcaa1c779b15fc8c0f9ecbb45ee2f7a1"
          },
          "contentType" : "application/vnd.oci.image.index.v1+json",
          "lastModified" : "2026-03-31T07:21:38.547+00:00",
          "lastDownloaded" : null,
          "uploader" : "emre",
          "uploaderIp" : "195.174.91.61",
          "fileSize" : 856,
          "blobCreated" : "2026-03-31T07:21:38.549+00:00",
          "blobStoreName" : "mystore",
          "docker" : { }
        } ]
      } ],
      "continuationToken" : null
    }
```
#### Deployment Verification via Browser

<img width="1788" height="1101" alt="image" src="https://github.com/user-attachments/assets/627f9d82-5902-4f9b-91dd-88691253dfb2" />

#### Command Summary
* `docker login [server:port]`: Authenticates the local Docker client against a remote registry.
* `docker tag [source] [target]`: Creates an alias for an existing image to match the routing structure of a remote repository.

</details>

******

<details>
<summary>Deploy docker application on a server</summary>
 <br />

### Demo Project: Docker Compose Application Integration

#### Project Overview
Demonstrated the integration of a custom Node.js application into an existing Docker Compose architecture. Modified the backend source code to replace local database routing (`localhost`) with internal Docker service resolution (`mongodb`). Successfully orchestrated and validated the multi-container environment in detached mode.

#### Infrastructure Configuration
Updated the declarative configuration file (`mongo.yaml`) to include the custom application service, mapping it to the previously pushed remote registry image and defining the necessary port bindings.
```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# cat mongo.yaml
    version: '3'
    services:

      my-app:
        image: 46.101.180.141:8083/my-app:1.0
        ports:
          - :3000:3000
      mongodb:
        image: mongo
        ports:
          - 27017:27017
        environment:
          - MONGO_INITDB_ROOT_USERNAME=admin
          - MONGO_INITDB_ROOT_PASSWORD=password
      mongo-express:
        image: mongo-express
        ports:
          - 8081:8081
        restart: always
        environment:
          - ME_CONFIG_MONGODB_ADMINUSERNAME=admin
          - ME_CONFIG_MONGODB_ADMINPASSWORD=password
          - ME_CONFIG_BASICAUTH_USERNAME=user
          - ME_CONFIG_BASICAUTH_PASSWORD=pass
          - ME_CONFIG_MONGODB_SERVER=mongodb
          - ME_CONFIG_MONGODB_URL=mongodb://mongodb:27017
```
#### Stack Deployment
Provisioned and started the defined services—including the backend application, database, and management UI—utilizing detached mode for background execution.
```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# docker-compose -f mongo.yaml up -d
    WARN[0000] /mnt/c/Users/emrea/js-app/app/mongo.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
    [+] up 4/4
     ✔ Network app_default           Created                                                                                                                                                             0.0s
     ✔ Container app-my-app-1        Started                                                                                                                                                             0.7s
     ✔ Container app-mongo-express-1 Started                                                                                                                                                             0.6s
     ✔ Container app-mongodb-1       Started                                                                                                                                                             0.7s
```
#### Infrastructure Verification & Log Monitoring
Tailed the unified logs of the Compose stack to verify the operational status of all services. Confirmed that the Node.js backend successfully resolved the database service name and started listening for incoming traffic without encountering connection refusal errors.
```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# docker-compose -f mongo.yaml logs -f
    WARN[0000] /mnt/c/Users/emrea/js-app/app/mongo.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
    mongo-express-1  | Waiting for mongodb:27017...
    mongodb-1        | {"t":{"$date":"2026-03-31T08:22:22.539+00:00"},"s":"I",  "c":"-",        "id":8991200, "ctx":"main","msg":"Shuffling initializers","attr":{"seed":2339129659}}
    ...
    my-app-1         | app listening on port 3000!
    ...
    mongodb-1        | {"t":{"$date":"2026-03-31T08:24:45.793+00:00"},"s":"W",  "c":"COMMAND",  "id":7024600, "ctx":"conn9","msg":"The collStats command is deprecated. For more information, see https://dochub.mongodb.org/core/collStats-deprecated"}
    my-app-1         | app listening on port 3000!
```

</details>

******


<details>
<summary>Docker Volumes Demo</summary>
 <br />

### Demo Project: Docker Compose Orchestration and Persistent Volumes

#### Project Overview
Demonstrated the deployment and management of a stateful multi-container application architecture. Integrated Docker named volumes for database persistence, performed network troubleshooting, and verified raw data access using both temporary utility containers and direct container execution. 

#### Infrastructure Configuration and Deployment
Configured a declarative `docker-compose.yaml` stack containing MongoDB and Mongo-Express. Implemented a persistent named volume (`mongo-data`) to ensure database records survive across container lifecycles and rebuilds.
```bash
    root@PC:/mnt/c/Users/emrea/js-app# cat docker-compose.yaml
    version: '3'
    services:
      mongodb:
        image: mongo
        ports:
          - 27017:27017
        environment:
          - MONGO_INITDB_ROOT_USERNAME=admin
          - MONGO_INITDB_ROOT_PASSWORD=password
        volumes:
          - mongo-data:/data/db
      mongo-express:
        image: mongo-express
        ports:
          - 8081:8081
        restart: always
		      environment:
	      	- ME_CONFIG_MONGODB_ADMINUSERNAME=admin
      		- ME_CONFIG_MONGODB_ADMINPASSWORD=password
	      	- ME_CONFIG_BASICAUTH_USERNAME=user
      		- ME_CONFIG_BASICAUTH_PASSWORD=pass
	      	- ME_CONFIG_MONGODB_SERVER=mongodb
      		- ME_CONFIG_MONGODB_URL=mongodb://mongodb:27017
     	volumes:
     	mongo-data:
		        
```
#### Container Lifecycle and Network Troubleshooting
Encountered a container crash loop (`Connection refused`) due to stale network configuration and locked ports. Remediated the issue by completely tearing down the environment to release the ports, and initializing a clean deployment. Verified successful authentication between the UI and database. Separately executed and gracefully terminated the backend Node.js application (`SIGINT`).
```bash
    root@PC:/mnt/c/Users/emrea/js-app# docker-compose -f docker-compose.yaml down
    WARN[0000] /mnt/c/Users/emrea/js-app/docker-compose.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
    [+] down 3/3
     ✔ Container js-app-mongodb-1       Removed                                                                                                                                                             0.5s
     ✔ Container js-app-mongo-express-1 Removed                                                                                                                                                             0.4s
     ✔ Network js-app_default           Removed                                                                                                                                                             0.3s
    root@PC:/mnt/c/Users/emrea/js-app# docker-compose -f docker-compose.yaml up
    ...
    mongodb-1        | {"t":{"$date":"2026-04-01T10:55:46.897+00:00"},"s":"I",  "c":"ACCESS",   "id":5286306, "ctx":"conn3","msg":"Successfully authenticated","attr":{"client":"172.20.0.3:44890"...
    mongo-express-1  | Mongo Express server listening at http://0.0.0.0:8081
    ...
    root@PC:/mnt/c/Users/emrea/js-app# cd app/
    root@PC:/mnt/c/Users/emrea/js-app/app# node server.js
    app listening on port 3000!
    ^C
```
#### Persistent Volume Inspection and Verification
Demonstrated deep-level access to Docker's isolated storage structure on the host machine. Utilized inspection tools to identify the physical mount point. Verified the physical presence of MongoDB's raw WiredTiger (`.wt`) files by mounting the data volume into an ephemeral Alpine Linux container, and cross-referenced the data by executing a shell directly inside the active database container.
```bash
	   root@PC:/var/lib/docker-desktop# docker volume ls
	   DRIVER    VOLUME NAME
	   local     2ab757f64de3d7985d9fb52d6bce93f117e9cd27b4fdfe971153459e6e2fe7a7
	   local     3dc8b4919bc0b0338362997f8cd6f2fcae1215c5dd9a35d853c7e5caf20f32d2
      ...
	   local     js-app_mongo-data

    root@PC:/var/lib/docker-desktop# docker volume inspect js-app_mongo-data
    [
        {
            "CreatedAt": "2026-04-01T10:55:40Z",
            "Driver": "local",
            "Mountpoint": "/var/lib/docker/volumes/js-app_mongo-data/_data",
            "Name": "js-app_mongo-data",
            "Options": null,
            "Scope": "local"
        }
    ]
    ...
    root@PC:/var/lib/docker-desktop# docker run -it --rm -v js-app_mongo-data:/data alpine sh
    / # ls -la /data
    total 472
    -rw-------    1 999      ping         86016 Apr  1 11:28 WiredTiger.wt
    -rw-------    1 999      ping         36864 Apr  1 10:59 _mdb_catalog.wt
    -rw-------    1 999      ping         20480 Apr  1 11:05 collection-09c78a08-f867-47ab-8320-b7edea2ac2a6.wt
    ...
    / # exit
    root@PC:/var/lib/docker-desktop# docker exec -it 8ddd6205ccc8 sh
    # ls /data/db
    WiredTiger.wt      _mdb_catalog.wt    collection-09c78a08-f867-47ab-8320-b7edea2ac2a6.wt  ...
```
#### UI Verification
Restarted the container and browsed DB to check if the changes i made was sadev.
<img width="1552" height="481" alt="image" src="https://github.com/user-attachments/assets/ec419252-fc3e-4c29-8e59-464f4f22b609" />


#### Command Summary

* `docker volume ls`: Lists all persistent storage volumes currently managed by the Docker engine.
* `docker volume inspect`: Retrieves detailed JSON metadata for a specific volume, exposing its physical host path.
* `docker run -it --rm -v [vol]:[path] alpine sh`: Spawns a temporary, interactive utility container to access and inspect isolated volume data directly, automatically destroying itself upon exit.
* `docker exec -it [container_id] sh`: Injects an interactive shell session inside an existing, running container to inspect its live internal file system.
 
</details>

******

<details>
<summary>Deploy Nexus as Docker Container</summary>
 <br />
 
**content will be here**
 
</details>

******

<details>
<summary>Docker Best Practices</summary>
 <br />
 
**content will be here**
 
</details>

******

