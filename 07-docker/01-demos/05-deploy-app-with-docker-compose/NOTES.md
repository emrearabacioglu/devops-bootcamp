# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Deploy Docker application on a server with Docker Compose

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
