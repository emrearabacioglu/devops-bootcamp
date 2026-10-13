# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Deploy Nexus as Docker container

### Demo Executed: Run Nexus in Docker on a droplet

#### Overview
Created a new Ubuntu droplet, installed Docker and ran Nexus as a container with a named volume for its data.

#### Docker Installation
Connected to the new droplet (attached to the existing firewall), updated the packages and installed Docker with snap:

```bash
    root@PC:/mnt/c/Users/emrea# ssh root@167.172.185.199
    Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.8.0-71-generic x86_64)
    ...
    root@ubuntu-docker-nexus:~# apt update
    Hit:1 http://security.ubuntu.com/ubuntu noble-security InRelease
    ...
    root@ubuntu-docker-nexus:~# snap install docker
    2026-04-01T12:33:19Z INFO Waiting for automatic snapd restart...
    docker 28.4.0 from Canonical✓ installed
```

#### Volume for Nexus Data
Created the `nexus-data` volume and checked its mount point. With snap Docker it's under `/var/snap/docker/...`:

```bash
    root@ubuntu-docker-nexus:~# docker volume create --name nexus-data
    nexus-data
    root@ubuntu-docker-nexus:~# docker inspect nexus-data
    [
        {
            "CreatedAt": "2026-04-01T12:36:10Z",
            "Driver": "local",
            "Labels": null,
            "Mountpoint": "/var/snap/docker/common/var-lib-docker/volumes/nexus-data/_data",
            "Name": "nexus-data",
            "Options": null,
            "Scope": "local"
        }
    ]
```

#### Running Nexus
Started Nexus in the background on port 8081 with the volume mounted to `/nexus-data`. Port 8081 is listening and the container is up:

```bash
    root@ubuntu-docker-nexus:~# docker run -d -p 8081:8081 --name nexus -v nexus-data:/nexus-data sonatype/nexus3
    ...
    Status: Downloaded newer image for sonatype/nexus3:latest
    25ede0c09d791109d3973499dfee73715ba5022814afdd6c04cd8c24f5482f2a
    ...
    root@ubuntu-docker-nexus:~# netstat -lnpt
    Active Internet connections (only servers)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
    tcp        0      0 0.0.0.0:8081            0.0.0.0:* LISTEN      3820/docker-proxy
    ...
    root@ubuntu-docker-nexus:~# docker ps
    CONTAINER ID   IMAGE             COMMAND                  CREATED              STATUS              PORTS                                       NAMES
    25ede0c09d79   sonatype/nexus3   "/opt/sonatype/nexus…"   About a minute ago   Up About a minute   0.0.0.0:8081->8081/tcp, [::]:8081->8081/tcp   nexus
```

#### Checking the Volume
The same folders are in the volume path on the host and in `/nexus-data` inside the container:

```bash
    root@ubuntu-docker-nexus:~# ls /var/snap/docker/common/var-lib-docker/volumes/nexus-data/_data
    blobs  clean_cache  db  downloads  etc  javaprefs  keystores  log  restore-from-backup  tmp
    root@ubuntu-docker-nexus:~# docker exec -it 25ede0c09d79 /bin/bash
    bash-5.1$ ls
    nexus  sonatype-work  start-nexus-repository-manager.sh
    bash-5.1$ cd /
    bash-5.1$ ls
    afs  boot  etc   lib    media  nexus-data  proc  run   srv  tmp  var
    bin  dev   home  lib64  mnt    opt         root  sbin  sys  usr
    bash-5.1$ ls nexus-data/
    blobs  clean_cache  db  downloads  etc  javaprefs  keystores  log  restore-from-backup  tmp
```
