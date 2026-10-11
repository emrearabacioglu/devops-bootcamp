# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Docker Compose - Run multiple Docker containers

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
