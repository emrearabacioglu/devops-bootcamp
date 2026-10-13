# Create Docker repository on Nexus and push to it

**Technologies:** Docker, Nexus, DigitalOcean, Linux

I used Nexus on my DigitalOcean Droplet as a private Docker registry and pushed the `my-app:1.0` image from the previous demo to it.

## Summary
1. In the Nexus UI I created a **docker (hosted)** repository `docker-hosted` with an HTTP connector on port 8083.
2. Created a role with access to this repository and gave it to my Nexus user `emre`.
3. Enabled **Docker Bearer Token Realm** in Nexus and opened port 8083 in the Droplet firewall.
4. Nexus uses plain HTTP, so I added `46.101.180.141:8083` to `insecure-registries` in Docker Desktop (Settings → Docker Engine).
5. Logged in with `docker login 46.101.180.141:8083`. The first try returned 401 Unauthorized, the second one worked.
6. Tagged the image as `46.101.180.141:8083/my-app:1.0`, pushed it and checked it with the Nexus REST API.

## Run
```bash
docker login 46.101.180.141:8083
docker tag my-app:1.0 46.101.180.141:8083/my-app:1.0
docker push 46.101.180.141:8083/my-app:1.0
curl -u emre:*** -X GET '46.101.180.141:8081/service/rest/v1/components?repository=docker-hosted'
```

## Result
The push worked and the REST API lists `my-app:1.0` in `docker-hosted`:
```
root@PC:/mnt/c/Users/emrea# docker push 46.101.180.141:8083/my-app:1.0
The push refers to repository [46.101.180.141:8083/my-app]
...
1.0: digest: sha256:e18236b5d15efc36509934d76863dc051371070b1b852dac07dec857822c596e size: 856
root@PC:/mnt/c/Users/emrea# curl -u emre:*** -X GET '46.101.180.141:8081/service/rest/v1/components?repository=docker-hosted'
{
  "items" : [ {
    "id" : "ZG9ja2VyLWhvc3RlZDo0ZjFiYmNkZA",
    "repository" : "docker-hosted",
    "format" : "docker",
    "group" : "",
    "name" : "my-app",
    "version" : "1.0",
...
      "uploader" : "emre",
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
