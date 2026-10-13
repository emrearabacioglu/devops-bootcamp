# Module 7 – Containers with Docker

## Contents

| # | Section | What's inside |
|---|---|---|
| 1 | Main Docker Commands | `run`, `pull`, `ps`, `stop`/`start`, port binding, and debugging with `logs`, `rm`, `exec` |
| 2 | Use Docker for local development | MongoDB + Mongo Express on a Docker network, Node.js app running locally |
| 3 | Docker Compose - Run multiple Docker containers | Same setup in one `mongo.yaml`, `up` and `down` |
| 4 | Dockerize Nodejs application | `Dockerfile` for the Node.js app, build and run `my-app:1.0` |
| 5 | Create Docker repository on Nexus and push to it | Docker hosted repo on Nexus, `docker login`, tag and push |
| 6 | Deploy Docker application on a server with Docker Compose | App image from Nexus added to the Compose file with MongoDB |
| 7 | Persist data with Docker Volumes | Named volume for MongoDB data, looking inside the volume |
| 8 | Deploy Nexus as Docker container | Docker on an Ubuntu droplet, Nexus container with a `nexus-data` volume |
| 9 | Docker Best Practices | Not written yet |

## Takeaways

- **Port conflict:** two containers can't use the same host port. The second `-p 6000:6379` failed with "port is already allocated", so I used `-p 6001:6379`. Different versions of the same image can run side by side (Postgres 13.10 and 14.7, Redis latest and 6.2).
- **Name conflict:** `--name redis-latest` failed because the name was already used by an old container. `docker rm` the old one first.
- **Shell in a container:** `docker exec -it <id or name> /bin/bash`. For `my-app` (`node:20-alpine`) I used `/bin/sh`.
- **Docker network:** containers on the same network reach each other by container name, e.g. `ME_CONFIG_MONGODB_SERVER=mongodb`.
- **Docker Compose:** `docker-compose -f <file> up` creates a default network (`<folder>_default`) and all containers, `down` removes them again. The `version` attribute is obsolete and only causes a warning.
- **App inside Compose:** the app has to connect to the DB with the service name `mongodb`, not `localhost`.
- **Push to Nexus:** the Docker repo needs its own connector port (8083), opened in the droplet firewall, plus "Docker Bearer Token Realm" in Nexus and the Nexus `IP:port` as an insecure registry in Docker Desktop. The image must be tagged as `<host>:<port>/<image>:<tag>` before `docker push`.
- **Nexus REST API:** `curl -u <user>:<pass> -X GET '<nexus>:8081/service/rest/v1/components?repository=docker-hosted'` lists what's in a repo.
- **Named volumes:** `mongo-data:/data/db` under the service plus a top-level `volumes:` entry. Compose adds the project name in front (`js-app_mongo-data`). The data was still there after restarting the container.
- **Look inside a volume:** `docker volume inspect` gives the mount point. `docker run -it --rm -v <volume>:/data alpine sh` mounts it into a throwaway container.
- **Crash loop with `Connection refused`:** an old network and ports still in use. `docker-compose down` and then `up` again fixed it.
- **Docker from snap:** volumes are under `/var/snap/docker/common/var-lib-docker/volumes/`, not `/var/lib/docker/volumes/`.

******

<details>
<summary>Main Docker Commands</summary>
 <br />

### Basic Commands

#### First Containers
Installed Docker on my local machine and ran two different versions of the Postgres image at the same time:

```bash
docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword postgres:13.10

docker run --name some-postgres-new -e POSTGRES_PASSWORD=mysecretpassword -d postgres:14.7

PS C:\Users\emrea> docker ps
CONTAINER ID   IMAGE            COMMAND                  CREATED          STATUS          PORTS      NAMES
c7056dad1904   postgres:14.7    "docker-entrypoint.s…"   4 seconds ago    Up 3 seconds    5432/tcp   some-postgres-new
ede91111c847   postgres:13.10   "docker-entrypoint.s…"   11 minutes ago   Up 11 minutes   5432/tcp   some-postgres
```

#### Images
Pulled the latest Redis image and listed the local images:

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

#### Start and Stop
Ran Redis in detached mode, stopped it, then listed all containers including the stopped one:

```bash
PS C:\Users\emrea> docker run -d redis
16cddd06392f2f1b554911b51b2c2b6e2acd6c6844fc3c98edadc696e16d6a83

PS C:\Users\emrea> docker stop 16cddd06392f
16cddd06392f

PS C:\Users\emrea> docker ps -a
CONTAINER ID   IMAGE   COMMAND                  CREATED         STATUS                      NAMES
16cddd06392f   redis   "docker-entrypoint.s…"   2 minutes ago   Exited (0) 23 seconds ago   gracious_cohen
```

#### Port Binding
Mapped host port 6000 to Redis port 6379. A second container on the same host port failed with "port is already allocated", so I ran `redis:6.2` on port 6001 instead:

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

#### Command Summary

* `docker pull`: download an image.
* `docker images`: list local images.
* `docker run`: start a container in the foreground.
* `docker run -d`: start a container in the background (detached).
* `docker stop`: stop a running container.
* `docker start`: start a stopped container again.
* `docker ps`: list running containers and their ports.
* `docker ps -a`: list all containers, including stopped ones.
* `docker run -p <host>:<container>`: bind a host port to a container port.

### Debug Commands

#### Logs
Checked the Redis startup logs using the container name:

```bash
PS C:\Users\emrea> docker logs redis-latest
Starting Redis Server
1:C 30 Mar 2026 08:08:05.297 * oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
...
1:M 30 Mar 2026 08:08:05.309 * Server initialized
1:M 30 Mar 2026 08:08:05.309 * Ready to accept connections tcp
```

#### Name Conflict
Starting a container with a name that was already in use failed. Removed the old container with `docker rm` and ran it again:

```bash
PS C:\Users\emrea> docker run -p 6000:6379 --name redis-latest -d redis
docker: Error response from daemon: Conflict. The container name "/redis-latest" is already in use...

PS C:\Users\emrea> docker rm 39c1098584d283a2cbe5fa018437be5f91c3efe4f8daba91adff6e0423ec6bb7
39c1098584d283a2cbe5fa018437be5f91c3efe4f8daba91adff6e0423ec6bb7

PS C:\Users\emrea> docker run -p 6000:6379 --name redis-latest -d redis
51015e2ff703884920419380a3fdaf86ea7a2756aedde49b513d763d510718d5
```

#### Shell Inside a Container
Opened a bash shell in the container and checked the environment variables. Then opened a shell in the `redis-older` container by name:

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

#### Command Summary

* `docker ps`: check running containers and port mappings.
* `docker logs`: show the logs of a container.
* `docker stop`: stop a container.
* `docker run --name <name> -p <host>:<container> -d`: run a named container in the background with a port mapping.
* `docker rm`: delete a container, e.g. to free up its name.
* `docker exec -it <container> /bin/bash`: open a shell inside a running container.

</details>

******

<details>
<summary>Demo Project: Use Docker for local development</summary>
 <br />

### Demo Executed: MongoDB and Mongo Express in Docker, Node.js app running locally

#### Overview
Ran MongoDB and Mongo Express as containers on their own Docker network and connected my local Node.js app to the database.

#### Pulling the Images
Pulled the `mongo` and `mongo-express` images:

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

#### Docker Network
Created a network so the two containers can reach each other by container name:

```bash
    root@PC:/mnt/c/Users/emrea# docker network create mongo-network
    16e494395ea4e77528ff206d9c2358b3e0e05095d8cd1bff5deffc15ec85439f
```

#### MongoDB Container
Started MongoDB in detached mode on the network, with the root user set through environment variables:

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

#### Mongo Express Container
Started Mongo Express on the same network. It connects to the database with the container name `mongodb`:

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

#### Checking the Containers
Both containers running, with their port mappings:

```bash
    root@PC:/mnt/c/Users/emrea/js-app# docker ps
    CONTAINER ID   IMAGE           COMMAND                  CREATED          STATUS          PORTS                                             NAMES
    abfc2ece56bd   mongo-express   "/sbin/tini -- /dock…"   10 minutes ago   Up 10 minutes   0.0.0.0:8081->8081/tcp, [::]:8081->8081/tcp       mongo-express
    d06a3779f6f0   mongo           "docker-entrypoint.s…"   20 minutes ago   Up 20 minutes   0.0.0.0:27017->27017/tcp, [::]:27017->27017/tcp   mongodb
```

#### Running the App
Started the Node.js app locally, listening on port 3000:

```bash
    root@PC:/mnt/c/Users/emrea/js-app# node app/server.js &
    [2] 8313
    root@PC:/mnt/c/Users/emrea/js-app# app listening on port 3000!
```

#### Database Logs
Followed the MongoDB logs while using the app. The logs show the new collections (`delete_me`, `users`) being created:

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
<summary>Demo Project: Docker Compose - Run multiple Docker containers</summary>
 <br />

### Demo Executed: Run MongoDB and Mongo Express with Docker Compose

#### Overview
Moved the two `docker run` commands from the previous demo into one Compose file, `mongo.yaml`. Started the stack, ran the Node.js app against it, then removed everything with `down`.

#### Compose File
`mongo.yaml` with both services, their ports and credentials:

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

#### Starting the Stack
`docker-compose up` created the `app_default` network and both containers. Compose warns that the `version` attribute is obsolete:

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

#### Checking the Stack and Running the App
From a second terminal, checked the network and the containers, then started the Node.js app:

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

#### Teardown
`docker-compose down` removed both containers and the network:

```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# docker-compose -f mongo.yaml down
    WARN[0000] /mnt/c/Users/emrea/js-app/app/mongo.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
    [+] down 3/3
     ✔ Container app-mongo-express-1 Removed                                                                                                                                                             0.4s
     ✔ Container app-mongodb-1       Removed                                                                                                                                                             0.5s
     ✔ Network app_default           Removed                                                                                                                                                             0.3s
```

#### Checking the Data in the UI
Checked in Mongo Express that the changes made in the app were saved in the database:

<img width="2554" height="942" alt="image" src="https://github.com/user-attachments/assets/0e450953-b119-408e-b1bb-ff013cf50b80" />

#### Command Summary

* `docker-compose -f <file> up`: create and start all services in the file.
* `docker-compose -f <file> down`: stop and remove the containers and the network created by `up`.

</details>

******

<details>
<summary>Demo Project: Dockerize Nodejs application</summary>
 <br />

### Demo Executed: Build a Docker image for the Node.js app

#### Overview
Wrote a `Dockerfile` for the Node.js app, built it as `my-app:1.0` and ran it. MongoDB and Mongo Express were started with Docker Compose like before.

#### Starting the Database
Started MongoDB and Mongo Express with the Compose file:

```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# docker-compose -f mongo.yaml up
    WARN[0000] /mnt/c/Users/emrea/js-app/app/mongo.yaml: the attribute `version` is obsolete...
    [+] up 3/3
     ✔ Network app_default           Created                                                                                                                                                             0.0s
     ✔ Container app-mongo-express-1 Created                                                                                                                                                             0.2s
     ✔ Container app-mongodb-1       Created                                                                                                                                                             0.1s
```

#### Dockerfile
Based on `node:20-alpine`. It sets the DB credentials as environment variables, copies the app to `/home/app`, installs the dependencies and starts the server:

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

#### Building the Image
Built and tagged the image as `my-app:1.0`. The first tries had path problems, which I fixed by changing the build context and the `WORKDIR`. The final build:

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

#### Running and Checking the Container
Ran the image in detached mode and opened a shell in it to check that the app files are in `/home/app`:

```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# docker run -d my-app:1.0
    059e8cd35881d2b85b3f5219df7cb094759705fa69c055e86d5552fedc0c5344

    root@PC:/mnt/c/Users/emrea# docker exec -it 059e8cd35881 /bin/sh
    /home/app # ls
    images             index.html         node_modules       package-lock.json  package.json       server.js
```

#### Command Summary

* `docker build -t <name:tag> .`: build an image from the `Dockerfile` in the current folder.
* `docker rmi <image>`: delete an image.
* `docker rm <container>`: delete a stopped container.
* `docker exec -it <container> /bin/sh`: open a shell in a running container.

</details>

******

<details>
<summary>Demo Project: Create Docker repository on Nexus and push to it</summary>
 <br />

### Demo Executed: Push the Node.js image to a Docker repository on Nexus

#### Overview
Used Nexus on my droplet as a private Docker registry. Created a Docker hosted repository, logged in from my local Docker, pushed `my-app:1.0` and checked it with the Nexus REST API.

#### Nexus and Docker Setup
- Created a Docker hosted repository in Nexus with a repository connector on port 8083.
- Created a role and a user for access.
- Opened port 8083 in the droplet firewall.
- Enabled "Docker Bearer Token Realm" in Nexus.
- Added the Nexus IP and port as an insecure registry in Docker Desktop's engine settings.

<img width="1584" height="1075" alt="image" src="https://github.com/user-attachments/assets/de4fb996-b582-4d2b-840c-6e9761c73d5c" />

<img width="1668" height="683" alt="image" src="https://github.com/user-attachments/assets/f1c82796-1769-492d-8704-12c095f3bb4a" />

#### Docker Login
Logged in to the Nexus Docker repository. The first try returned 401 Unauthorized, the second one worked:

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

#### Tagging the Image
Tagged `my-app:1.0` with the Nexus address so Docker knows where to push it:

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

#### Pushing the Image
Pushed the tagged image to Nexus:

```bash
    root@PC:/mnt/c/Users/emrea# docker push 46.101.180.141:8083/my-app:1.0
    The push refers to repository [46.101.180.141:8083/my-app]
    ...
    1.0: digest: sha256:e18236b5d15efc36509934d76863dc051371070b1b852dac07dec857822c596e size: 856
```

#### Checking with the REST API
Listed the components in the `docker-hosted` repository with the Nexus REST API. `my-app:1.0` is there:

```bash
    root@PC:/mnt/c/Users/emrea# curl -u emre:*** -X GET '46.101.180.141:8081/service/rest/v1/components?repository=docker-hosted'
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
          "uploaderIp" : "<my-ip>",
          "fileSize" : 856,
          "blobCreated" : "2026-03-31T07:21:38.549+00:00",
          "blobStoreName" : "mystore",
          "docker" : { }
        } ]
      } ],
      "continuationToken" : null
    }
```

#### Checking in the Browser
The image in the Nexus UI:

<img width="1788" height="1101" alt="image" src="https://github.com/user-attachments/assets/627f9d82-5902-4f9b-91dd-88691253dfb2" />

#### Command Summary

* `docker login <host:port>`: log in to a registry.
* `docker tag <source> <target>`: give an image a new name, e.g. with the registry address in front so it can be pushed there.

</details>

******

<details>
<summary>Demo Project: Deploy Docker application on a server with Docker Compose</summary>
 <br />

### Demo Executed: Run my-app from Nexus together with MongoDB in Docker Compose

#### Overview
Added the app image from Nexus to the Compose file, next to MongoDB and Mongo Express. In the app code I changed the database host from `localhost` to the service name `mongodb`, because inside Compose the containers reach each other by service name.

#### Compose File
Added the `my-app` service with the image pushed to Nexus:

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

#### Starting the Stack
Started all three services in detached mode:

```bash
    root@PC:/mnt/c/Users/emrea/js-app/app# docker-compose -f mongo.yaml up -d
    WARN[0000] /mnt/c/Users/emrea/js-app/app/mongo.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
    [+] up 4/4
     ✔ Network app_default           Created                                                                                                                                                             0.0s
     ✔ Container app-my-app-1        Started                                                                                                                                                             0.7s
     ✔ Container app-mongo-express-1 Started                                                                                                                                                             0.6s
     ✔ Container app-mongodb-1       Started                                                                                                                                                             0.7s
```

#### Checking the Logs
Followed the logs of the whole stack. The app starts and listens on port 3000 with no connection errors:

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
<summary>Demo Project: Persist data with Docker Volumes</summary>
 <br />

### Demo Executed: Keep MongoDB data in a named volume

#### Overview
Added a named volume (`mongo-data`) for MongoDB in the Compose file so the data stays when the container is restarted. Then found the volume on the host and looked at the files inside it.

#### Compose File with a Volume
`docker-compose.yaml` with `mongo-data` mounted to `/data/db`:

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

#### Fixing a Crash Loop
The containers kept failing with `Connection refused` because of an old network and ports that were still in use. Ran `docker-compose down` to remove everything and started it again. After that Mongo Express could authenticate to MongoDB. Then started the Node.js app and stopped it with Ctrl+C:

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

#### Looking Inside the Volume
Listed the volumes and used `docker volume inspect` to see where `js-app_mongo-data` is stored. To see the files, I mounted the volume into a temporary Alpine container. MongoDB's data files (`.wt`) are there, and the same files are in `/data/db` inside the running MongoDB container:

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

#### Checking the Data in the UI
Restarted the container and checked in Mongo Express that my changes were still saved:

<img width="1552" height="481" alt="image" src="https://github.com/user-attachments/assets/ec419252-fc3e-4c29-8e59-464f4f22b609" />

#### Command Summary

* `docker volume ls`: list volumes.
* `docker volume inspect <volume>`: show volume details, including the mount point on the host.
* `docker run -it --rm -v <volume>:<path> alpine sh`: start a temporary container with the volume mounted. It's deleted on exit.
* `docker exec -it <container> sh`: open a shell in a running container.

</details>

******

<details>
<summary>Demo Project: Deploy Nexus as Docker container</summary>
 <br />

### Demo Executed: Run Nexus in Docker on a droplet

#### Overview
Created a new Ubuntu droplet, installed Docker and ran Nexus as a container with a named volume for its data.

#### Docker Installation
Connected to the new droplet (attached to the existing firewall), updated the packages and installed Docker with snap:

```bash
    root@PC:/mnt/c/Users/emrea# ssh root@167.172.185.199
    Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.8.0-71-generic x86_64)
    ...
    root@ubuntu-docker-nexus:~# apt update
    Hit:1 http://security.ubuntu.com/ubuntu noble-security InRelease
    ...
    root@ubuntu-docker-nexus:~# snap install docker
    2026-04-01T12:33:19Z INFO Waiting for automatic snapd restart...
    docker 28.4.0 from Canonical✓ installed
```

#### Volume for Nexus Data
Created the `nexus-data` volume and checked its mount point. With snap Docker it's under `/var/snap/docker/...`:

```bash
    root@ubuntu-docker-nexus:~# docker volume create --name nexus-data
    nexus-data
    root@ubuntu-docker-nexus:~# docker inspect nexus-data
    [
        {
            "CreatedAt": "2026-04-01T12:36:10Z",
            "Driver": "local",
            "Labels": null,
            "Mountpoint": "/var/snap/docker/common/var-lib-docker/volumes/nexus-data/_data",
            "Name": "nexus-data",
            "Options": null,
            "Scope": "local"
        }
    ]
```

#### Running Nexus
Started Nexus in the background on port 8081 with the volume mounted to `/nexus-data`. Port 8081 is listening and the container is up:

```bash
    root@ubuntu-docker-nexus:~# docker run -d -p 8081:8081 --name nexus -v nexus-data:/nexus-data sonatype/nexus3
    ...
    Status: Downloaded newer image for sonatype/nexus3:latest
    25ede0c09d791109d3973499dfee73715ba5022814afdd6c04cd8c24f5482f2a
    ...
    root@ubuntu-docker-nexus:~# netstat -lnpt
    Active Internet connections (only servers)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
    tcp        0      0 0.0.0.0:8081            0.0.0.0:* LISTEN      3820/docker-proxy
    ...
    root@ubuntu-docker-nexus:~# docker ps
    CONTAINER ID   IMAGE             COMMAND                  CREATED              STATUS              PORTS                                       NAMES
    25ede0c09d79   sonatype/nexus3   "/opt/sonatype/nexus…"   About a minute ago   Up About a minute   0.0.0.0:8081->8081/tcp, [::]:8081->8081/tcp   nexus
```

#### Checking the Volume
The same folders are in the volume path on the host and in `/nexus-data` inside the container:

```bash
    root@ubuntu-docker-nexus:~# ls /var/snap/docker/common/var-lib-docker/volumes/nexus-data/_data
    blobs  clean_cache  db  downloads  etc  javaprefs  keystores  log  restore-from-backup  tmp
    root@ubuntu-docker-nexus:~# docker exec -it 25ede0c09d79 /bin/bash
    bash-5.1$ ls
    nexus  sonatype-work  start-nexus-repository-manager.sh
    bash-5.1$ cd /
    bash-5.1$ ls
    afs  boot  etc   lib    media  nexus-data  proc  run   srv  tmp  var
    bin  dev   home  lib64  mnt    opt         root  sbin  sys  usr
    bash-5.1$ ls nexus-data/
    blobs  clean_cache  db  downloads  etc  javaprefs  keystores  log  restore-from-backup  tmp
```

</details>

******

<details>
<summary>Docker Best Practices</summary>
 <br />

**content will be here**

</details>

******
