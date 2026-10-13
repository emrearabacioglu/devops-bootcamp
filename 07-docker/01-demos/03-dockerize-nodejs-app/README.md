# Dockerize Nodejs application

**Technologies:** Docker, Node.js

I wrote a `Dockerfile` for the Node.js app in `app/`, built it as the image `my-app:1.0` and ran it as a container.

## Summary
1. Started MongoDB and Mongo Express with Docker Compose like in the previous demo.
2. Wrote the `Dockerfile`: base image `node:20-alpine`, sets `MONGO_DB_USERNAME` / `MONGO_DB_PWD` as environment variables, copies `app/` to `/home/app`, sets it as `WORKDIR`, runs `npm install` and starts `node server.js`.
3. In this version `app/server.js` connects to MongoDB with the service name `mongodb` (`mongoUrlDockerCompose`), so it works when the app runs as a container next to the database.
4. Built the image with `docker build -t my-app:1.0 .`. The first tries had path problems, which I fixed by changing the build context and the `WORKDIR`.
5. Ran the image with `docker run -d my-app:1.0` and opened a shell in the container with `docker exec -it` to check the app files in `/home/app`.

## Run
```bash
docker build -t my-app:1.0 .
docker run -d my-app:1.0
```

## Result
The image builds, the container runs and the app files are in `/home/app`:
```
root@PC:/mnt/c/Users/emrea/js-app/app# docker build -t my-app:1.0 .
[+] Building 14.8s (11/11) FINISHED                                                               docker:default
...
 => [5/5] RUN npm install                                                                                   9.9s
 => exporting to image                                                                                      3.4s
 => => naming to docker.io/library/my-app:1.0                                                               0.0s
...
root@PC:/mnt/c/Users/emrea/js-app/app# docker run -d my-app:1.0
059e8cd35881d2b85b3f5219df7cb094759705fa69c055e86d5552fedc0c5344
...
root@PC:/mnt/c/Users/emrea# docker exec -it 059e8cd35881 /bin/sh
/home/app # ls
images             index.html         node_modules       package-lock.json  package.json       server.js
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
