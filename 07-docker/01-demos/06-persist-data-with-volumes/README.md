# Persist data with Docker Volumes

**Technologies:** Docker, Node.js, MongoDB

Without a volume, the MongoDB data is lost when the container is removed. I added a named volume `mongo-data` to the Compose file so the data stays.

## Summary
1. In `docker-compose.yaml` I added the named volume `mongo-data` (driver `local`) and mounted it to `/data/db`, which is MongoDB's data folder.
2. The first start went into a crash loop with `Connection refused` because of an old network and ports still in use. I fixed it with `docker-compose -f docker-compose.yaml down` and started it again with `up`.
3. Started the Node.js app with `node server.js` and added some data.
4. Found the volume with `docker volume ls` and `docker volume inspect js-app_mongo-data`, then mounted it into a temporary Alpine container to see the MongoDB data files (`.wt`). The same files are in `/data/db` in the running MongoDB container.
5. Restarted the container and checked in Mongo Express that my changes were still saved.

## Run
```bash
docker-compose -f docker-compose.yaml up
docker volume inspect js-app_mongo-data
docker run -it --rm -v js-app_mongo-data:/data alpine sh
```

## Result
The volume exists on the host and holds the MongoDB data files:
```
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
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
