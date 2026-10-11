# Docker Compose - Run multiple Docker containers

**Technologies:** Docker, MongoDB, MongoExpress

I moved the two `docker run` commands from the previous demo into one Docker Compose file, `mongo.yaml`, and started MongoDB and Mongo Express with it.

## Summary
1. Wrote `mongo.yaml` with two services, `mongodb` (port 27017) and `mongo-express` (port 8081, `restart: always`), with the same environment variables as in the `docker run` commands.
2. Started both containers with `docker-compose -f mongo.yaml up`. Compose created the `app_default` network for them, so no manual `docker network create` was needed.
3. Checked the network with `docker network ls` and the containers with `docker ps`, then started the Node.js app against the database.
4. Checked in Mongo Express that the data from the app was saved.
5. Removed the containers and the network with `docker-compose -f mongo.yaml down`.

## Run
```bash
docker-compose -f mongo.yaml up
docker-compose -f mongo.yaml down
```

## Result
Compose started both containers on its own network, and `down` removed them again:
```
root@PC:/mnt/c/Users/emrea# docker network ls
NETWORK ID     NAME            DRIVER    SCOPE
fa6033aaed99   app_default     bridge    local
...
root@PC:/mnt/c/Users/emrea# docker ps
CONTAINER ID   IMAGE           COMMAND                  CREATED          STATUS          PORTS                                             NAMES
37435ab2639d   mongo           "docker-entrypoint.s…"   3 minutes ago    Up 3 minutes    0.0.0.0:27017->27017/tcp, [::]:27017->27017/tcp   app-mongodb-1
4f73371e9d40   mongo-express   "/sbin/tini -- /dock…"   3 minutes ago    Up 3 minutes    0.0.0.0:8081->8081/tcp, [::]:8081->8081/tcp       app-mongo-express-1
...
root@PC:/mnt/c/Users/emrea/js-app/app# docker-compose -f mongo.yaml down
...
[+] down 3/3
 ✔ Container app-mongo-express-1 Removed                                                                                                                                                             0.4s
 ✔ Container app-mongodb-1       Removed                                                                                                                                                             0.5s
 ✔ Network app_default           Removed                                                                                                                                                             0.3s
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
