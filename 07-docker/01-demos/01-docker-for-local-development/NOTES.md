# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Use Docker for local development

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
