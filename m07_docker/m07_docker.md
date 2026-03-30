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

</details>

******

<details>
<summary>Debug Commands</summary>
 <br />

**content will be here**
 
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

