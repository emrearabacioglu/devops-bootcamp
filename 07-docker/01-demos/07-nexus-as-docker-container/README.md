# Deploy Nexus as Docker container

**Technologies:** Docker, Nexus, DigitalOcean, Linux

Instead of installing Nexus by hand like in module 6, I ran it as a Docker container on a new DigitalOcean Droplet. A named volume keeps the Nexus data.

## Summary
1. Created a new Ubuntu Droplet, attached it to my existing firewall and connected with `ssh root@167.172.185.199`.
2. Ran `apt update` and installed Docker with `snap install docker`.
3. Created the volume `nexus-data` with `docker volume create`. With snap Docker it is stored under `/var/snap/docker/common/var-lib-docker/volumes/`.
4. Started Nexus with `docker run -d -p 8081:8081 --name nexus -v nexus-data:/nexus-data sonatype/nexus3`.
5. Checked with `netstat -lnpt` and `docker ps` that port 8081 is open and the container is up.
6. Checked that the same Nexus folders are in the volume path on the host and in `/nexus-data` inside the container. The admin password for the first login is in `/nexus-data/admin.password`.

## Run
```bash
snap install docker
docker volume create --name nexus-data
docker run -d -p 8081:8081 --name nexus -v nexus-data:/nexus-data sonatype/nexus3
```

## Result
Nexus is running on port 8081 and its data is in the volume:
```
root@ubuntu-docker-nexus:~# netstat -lnpt
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:8081            0.0.0.0:* LISTEN      3820/docker-proxy
...
root@ubuntu-docker-nexus:~# docker ps
CONTAINER ID   IMAGE             COMMAND                  CREATED              STATUS              PORTS                                       NAMES
25ede0c09d79   sonatype/nexus3   "/opt/sonatype/nexus…"   About a minute ago   Up About a minute   0.0.0.0:8081->8081/tcp, [::]:8081->8081/tcp   nexus
root@ubuntu-docker-nexus:~# ls /var/snap/docker/common/var-lib-docker/volumes/nexus-data/_data
blobs  clean_cache  db  downloads  etc  javaprefs  keystores  log  restore-from-backup  tmp
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
