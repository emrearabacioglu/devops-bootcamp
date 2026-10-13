# Use Docker for local development

**Technologies:** Docker, Node.js, MongoDB, MongoExpress

I ran MongoDB and Mongo Express as Docker containers on my PC and connected the Node.js app in `app/` to the database.

## Summary
1. Pulled the `mongo` and `mongo-express` images and created a Docker network `mongo-network`, so the containers can reach each other by name.
2. Started the `mongodb` container on that network with port 27017 and the root user set with `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD`.
3. Started the `mongo-express` container on the same network with port 8081. It connects to the database by the container name (`ME_CONFIG_MONGODB_SERVER=mongodb`).
4. Started the app with `node app/server.js` (port 3000). `app/server.js` connects to MongoDB on `localhost:27017` (`mongoUrlLocal`).
5. Followed the MongoDB logs with `docker logs -f` while using the app and saw the collections in the `user-account` database being created.

## Result
Both containers running, the app started and MongoDB created the `users` collection:
```
root@PC:/mnt/c/Users/emrea/js-app# docker ps
CONTAINER ID   IMAGE           COMMAND                  CREATED          STATUS          PORTS                                             NAMES
abfc2ece56bd   mongo-express   "/sbin/tini -- /dock…"   10 minutes ago   Up 10 minutes   0.0.0.0:8081->8081/tcp, [::]:8081->8081/tcp       mongo-express
d06a3779f6f0   mongo           "docker-entrypoint.s…"   20 minutes ago   Up 20 minutes   0.0.0.0:27017->27017/tcp, [::]:27017->27017/tcp   mongodb
...
root@PC:/mnt/c/Users/emrea/js-app# app listening on port 3000!
...
{"t":{"$date":"2026-03-30T14:47:52.502+00:00"},"s":"I",  "c":"STORAGE",  "id":20320,   "ctx":"conn3","msg":"createCollection","attr":{"namespace":"user-account.users","uuidDisposition":"generated","uuid":{"uuid":{"$uuid":"df633f76-4d26-4c7f-a825-b94a6bea7912"}},"options":{}}}
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
