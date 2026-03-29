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
<summary>Docker vs. Virtual Machine</summary>
 <br />

**content will be here**
 
</details>

******

<details>
<summary>Docker Architecture and components</summary>
 <br />

**content will be here**
 
</details>

******

<details>
<summary>Main Docker Commands</summary>
 <br />

**content will be here**
 
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

Deploy Nexus as Docker Container

Docker Best Practices
