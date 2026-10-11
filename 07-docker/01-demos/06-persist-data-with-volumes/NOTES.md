# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Persist data with Docker Volumes

### Demo Executed: Keep MongoDB data in a named volume

#### Overview
Added a named volume (`mongo-data`) for MongoDB in the Compose file so the data stays when the container is restarted. Then found the volume on the host and looked at the files inside it.

#### Compose File with a Volume
`docker-compose.yaml` with `mongo-data` mounted to `/data/db`:

```bash
    root@PC:/mnt/c/Users/emrea/js-app# cat docker-compose.yaml
    version: '3'
    services:
      mongodb:
        image: mongo
        ports:
          - 27017:27017
        environment:
          - MONGO_INITDB_ROOT_USERNAME=admin
          - MONGO_INITDB_ROOT_PASSWORD=password
        volumes:
          - mongo-data:/data/db
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
     	volumes:
     	mongo-data:
		        
```

#### Fixing a Crash Loop
The containers kept failing with `Connection refused` because of an old network and ports that were still in use. Ran `docker-compose down` to remove everything and started it again. After that Mongo Express could authenticate to MongoDB. Then started the Node.js app and stopped it with Ctrl+C:

```bash
    root@PC:/mnt/c/Users/emrea/js-app# docker-compose -f docker-compose.yaml down
    WARN[0000] /mnt/c/Users/emrea/js-app/docker-compose.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
    [+] down 3/3
     ✔ Container js-app-mongodb-1       Removed                                                                                                                                                             0.5s
     ✔ Container js-app-mongo-express-1 Removed                                                                                                                                                             0.4s
     ✔ Network js-app_default           Removed                                                                                                                                                             0.3s
    root@PC:/mnt/c/Users/emrea/js-app# docker-compose -f docker-compose.yaml up
    ...
    mongodb-1        | {"t":{"$date":"2026-04-01T10:55:46.897+00:00"},"s":"I",  "c":"ACCESS",   "id":5286306, "ctx":"conn3","msg":"Successfully authenticated","attr":{"client":"172.20.0.3:44890"...
    mongo-express-1  | Mongo Express server listening at http://0.0.0.0:8081
    ...
    root@PC:/mnt/c/Users/emrea/js-app# cd app/
    root@PC:/mnt/c/Users/emrea/js-app/app# node server.js
    app listening on port 3000!
    ^C
```

#### Looking Inside the Volume
Listed the volumes and used `docker volume inspect` to see where `js-app_mongo-data` is stored. To see the files, I mounted the volume into a temporary Alpine container. MongoDB's data files (`.wt`) are there, and the same files are in `/data/db` inside the running MongoDB container:

```bash
	   root@PC:/var/lib/docker-desktop# docker volume ls
	   DRIVER    VOLUME NAME
	   local     2ab757f64de3d7985d9fb52d6bce93f117e9cd27b4fdfe971153459e6e2fe7a7
	   local     3dc8b4919bc0b0338362997f8cd6f2fcae1215c5dd9a35d853c7e5caf20f32d2
      ...
	   local     js-app_mongo-data

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
    ...
    / # exit
    root@PC:/var/lib/docker-desktop# docker exec -it 8ddd6205ccc8 sh
    # ls /data/db
    WiredTiger.wt      _mdb_catalog.wt    collection-09c78a08-f867-47ab-8320-b7edea2ac2a6.wt  ...
```

#### Checking the Data in the UI
Restarted the container and checked in Mongo Express that my changes were still saved:

<img width="1552" height="481" alt="image" src="https://github.com/user-attachments/assets/ec419252-fc3e-4c29-8e59-464f4f22b609" />

#### Command Summary

* `docker volume ls`: list volumes.
* `docker volume inspect <volume>`: show volume details, including the mount point on the host.
* `docker run -it --rm -v <volume>:<path> alpine sh`: start a temporary container with the volume mounted. It's deleted on exit.
* `docker exec -it <container> sh`: open a shell in a running container.
