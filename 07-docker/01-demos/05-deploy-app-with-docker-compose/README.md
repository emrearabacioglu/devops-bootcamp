# Deploy Docker application on a server with Docker Compose

**Technologies:** Docker, Nexus (used instead of Amazon ECR), Node.js, MongoDB, MongoExpress

I added my app image from the private Nexus registry to the Compose file and started it together with MongoDB and Mongo Express. In my notes I ran this on my PC (`root@PC`), not on a separate remote server.

## Summary
1. In the app code I changed the MongoDB host from `localhost` to the service name `mongodb`, because inside Compose the containers reach each other by service name. Then I built the image again and pushed it to Nexus as `46.101.180.141:8083/my-app:1.0`.
2. Added the `my-app` service with that image and port 3000 to `mongo.yaml`, next to the `mongodb` and `mongo-express` services.
3. Logged in to the private registry with `docker login 46.101.180.141:8083` so the image can be pulled.
4. Started all three services with `docker-compose -f mongo.yaml up -d` and followed the logs with `docker-compose -f mongo.yaml logs -f`.

## Run
```bash
docker login 46.101.180.141:8083
docker-compose -f mongo.yaml up -d
docker-compose -f mongo.yaml logs -f
```

## Result
All three containers started and the app listens on port 3000:
```
root@PC:/mnt/c/Users/emrea/js-app/app# docker-compose -f mongo.yaml up -d
...
[+] up 4/4
 ✔ Network app_default           Created                                                                                                                                                             0.0s
 ✔ Container app-my-app-1        Started                                                                                                                                                             0.7s
 ✔ Container app-mongo-express-1 Started                                                                                                                                                             0.6s
 ✔ Container app-mongodb-1       Started                                                                                                                                                             0.7s
root@PC:/mnt/c/Users/emrea/js-app/app# docker-compose -f mongo.yaml logs -f
...
my-app-1         | app listening on port 3000!
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
