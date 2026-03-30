# Containers with Docker

******

<details>
<summary>Container vs Image</summary>
 <br />

Installed Docker on local machine

Demo executed - run two different Versions of Postgres Docker Images:

```bash

docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword postgres:13.10

docker run --name some-postgres-new -e POSTGRES_PASSWORD=mysecretpassword -d postgres:14.7

PS C:\Users\emrea> docker ps
CONTAINER ID   IMAGE            COMMAND                  CREATED          STATUS          PORTS      NAMES
c7056dad1904   postgres:14.7    "docker-entrypoint.s…"   4 seconds ago    Up 3 seconds    5432/tcp   some-postgres-new
ede91111c847   postgres:13.10   "docker-entrypoint.s…"   11 minutes ago   Up 11 minutes   5432/tcp   some-postgres

```
 
</details>

******

<details>
<summary>Main Docker Commands</summary>
 <br />
 
#### Image Management
Demonstrated fetching the latest Redis image and verifying local image storage.

```bash
PS C:\Users\emrea> docker pull redis
Using default tag: latest
latest: Pulling from library/redis
...
Status: Downloaded newer image for redis:latest

PS C:\Users\emrea> docker images
IMAGE             ID             DISK USAGE   CONTENT SIZE
postgres:14.7     5ac16ee31134        541MB          138MB
redis:latest      009cc37796fb        204MB         55.3MB
```
#### Container Lifecycle
Executed containers in detached mode and managed start/stop state transitions.
```bash
PS C:\Users\emrea> docker run -d redis
16cddd06392f2f1b554911b51b2c2b6e2acd6c6844fc3c98edadc696e16d6a83

PS C:\Users\emrea> docker stop 16cddd06392f
16cddd06392f

PS C:\Users\emrea> docker ps -a
CONTAINER ID   IMAGE   COMMAND                  CREATED         STATUS                      NAMES
16cddd06392f   redis   "docker-entrypoint.s…"   2 minutes ago   Exited (0) 23 seconds ago   gracious_cohen
```

#### Port Binding & Conflict Resolution
Configured host-to-container port mapping and resolved an allocation conflict by deploying a secondary database version on an alternate port.

```bash
PS C:\Users\emrea> docker run -p 6000:6379 -d redis
f71b5d49234c017891ce9870d82cba2eee9bc1be0ab7b80e6e4be466efa9530d

PS C:\Users\emrea> docker run -p 6000:6379 -d redis:6.2
docker: Error response from daemon: failed to set up container networking... Bind for 0.0.0.0:6000 failed: port is already allocated

PS C:\Users\emrea> docker run -p 6001:6379 -d redis:6.2
37ce9f8db5c64f4ecf96a84bae62e3f46e833a2f25832c619f9d1846053fc19a

PS C:\Users\emrea> docker ps
CONTAINER ID   IMAGE       STATUS              PORTS                                         NAMES
37ce9f8db5c6   redis:6.2   Up 7 seconds        0.0.0.0:6001->6379/tcp, [::]:6001->6379/tcp   gifted_tu
f71b5d49234c   redis       Up About a minute   0.0.0.0:6000->6379/tcp, [::]:6000->6379/tcp   intelligent_swartz
```

#### Docker Command Referance

* `docker pull`: Fetched images from the registry.
* `docker images`: Audited local images and disk usage.
* `docker run`: Executed a container in the foreground.
* `docker run -d`: Deployed a container in detached mode.
* `docker stop`: Halted an active container.
* `docker start`: Restarted an exited container.
* `docker ps`: Monitored active containers and ports.
* `docker ps -a`: Listed lifecycle history of all containers.
* `docker run -p`: Configured host-to-container port binding.

</details>

******

<details>
<summary>Debug Commands</summary>
 <br />

#### Log Analysis
Audited container startup sequences and background logs using both IDs and assigned names.

```bash
PS C:\Users\emrea> docker logs redis-latest
Starting Redis Server
1:C 30 Mar 2026 08:08:05.297 * oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
...
1:M 30 Mar 2026 08:08:05.309 * Server initialized
1:M 30 Mar 2026 08:08:05.309 * Ready to accept connections tcp
```

#### Conflict Resolution
Cleared container naming conflicts by removing the overlapping instance and redeploying the service.

```bash
PS C:\Users\emrea> docker run -p 6000:6379 --name redis-latest -d redis
docker: Error response from daemon: Conflict. The container name "/redis-latest" is already in use...

PS C:\Users\emrea> docker rm 39c1098584d283a2cbe5fa018437be5f91c3efe4f8daba91adff6e0423ec6bb7
39c1098584d283a2cbe5fa018437be5f91c3efe4f8daba91adff6e0423ec6bb7

PS C:\Users\emrea> docker run -p 6000:6379 --name redis-latest -d redis
51015e2ff703884920419380a3fdaf86ea7a2756aedde49b513d763d510718d5
```

#### Interactive Shell (Exec)
Accessed the internal bash shell to inspect file systems and environment variables.

```bash
PS C:\Users\emrea> docker exec -it 51015e2ff703 /bin/bash
root@51015e2ff703:/data# cd /
root@51015e2ff703:/# env
HOSTNAME=51015e2ff703
PWD=/
HOME=/root
TERM=xterm
SHLVL=1
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
_=/usr/bin/env
OLDPWD=/data
root@51015e2ff703:/# exit
exit

PS C:\Users\emrea> docker exec -it redis-older /bin/bash
root@26cb48b6efb7:/data# exit

```
#### Docker Debugging Command Reference

* `docker ps`: Monitored active containers and verified port mappings.
* `docker logs`: Retrieved background execution and initialization logs.
* `docker stop`: Halted specific running containers.
* `docker run`: Deployed named containers in detached mode with specific port configurations.
* `docker rm`: Deleted specific containers to resolve naming conflicts.
* `docker exec`: Established an interactive bash shell session inside a running container for inspection.


</details>

******

<details>
<summary>Docker Demo - Project Overview</summary>
 <br />

**content will be here**
 
</details>

******

<details>
<summary>Developing with Docker</summary>
 <br />

**content will be here**
 
</details>

******

<details>
<summary>Docker Compose - Run multiple Docker containers</summary>
 <br />

**content will be here**
 
</details>

******

<details>
<summary>Dockerfile - Build your own Docker Image</summary>
 <br />

**content will be here**
 
</details>

******

<details>
<summary>Private Docker Repository</summary>
 <br />

**content will be here**
 
</details>

******

<details>
<summary>Deploy docker application on a server</summary>
 <br />

**content will be here**
 
</details>

******

<details>
<summary>Docker Volumes - Persisting Data</summary>
 <br />

**content will be here**
 
</details>

******

<details>
<summary>Docker Volumes Demo</summary>
 <br />

**content will be here**
 
</details>

******

<details>
<summary>Deploy Nexus as Docker Container</summary>
 <br />
 
**content will be here**
 
</details>

******

<details>
<summary>Docker Best Practices</summary>
 <br />
 
**content will be here**
 
</details>

******

