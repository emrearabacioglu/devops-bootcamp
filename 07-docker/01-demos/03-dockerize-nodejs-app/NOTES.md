# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Dockerize Nodejs application

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
