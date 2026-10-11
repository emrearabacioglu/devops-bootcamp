# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Create Docker repository on Nexus and push to it

### Demo Executed: Push the Node.js image to a Docker repository on Nexus

#### Overview
Used Nexus on my droplet as a private Docker registry. Created a Docker hosted repository, logged in from my local Docker, pushed `my-app:1.0` and checked it with the Nexus REST API.

#### Nexus and Docker Setup
- Created a Docker hosted repository in Nexus with a repository connector on port 8083.
- Created a role and a user for access.
- Opened port 8083 in the droplet firewall.
- Enabled "Docker Bearer Token Realm" in Nexus.
- Added the Nexus IP and port as an insecure registry in Docker Desktop's engine settings.

<img width="1584" height="1075" alt="image" src="https://github.com/user-attachments/assets/de4fb996-b582-4d2b-840c-6e9761c73d5c" />

<img width="1668" height="683" alt="image" src="https://github.com/user-attachments/assets/f1c82796-1769-492d-8704-12c095f3bb4a" />

#### Docker Login
Logged in to the Nexus Docker repository. The first try returned 401 Unauthorized, the second one worked:

```bash
    root@PC:/mnt/c/Users/emrea# docker login 46.101.180.141:8083
    Username: emre
    Password:
    Error response from daemon: login attempt to http://46.101.180.141:8083/v2/ failed with status: 401 Unauthorized
    root@PC:/mnt/c/Users/emrea# docker login 46.101.180.141:8083
    Username: emre
    Password:
    Login Succeeded
```

#### Tagging the Image
Tagged `my-app:1.0` with the Nexus address so Docker knows where to push it:

```bash
    root@PC:/mnt/c/Users/emrea# docker images
                                                                                                                     i Info →   U  In Use
    IMAGE                  ID             DISK USAGE   CONTENT SIZE   EXTRA
    ...
    my-app:1.0             e18236b5d15e        325MB         70.2MB   U
    ...
    root@PC:/mnt/c/Users/emrea# docker tag my-app:1.0 46.101.180.141:8083/my-app:1.0
    root@PC:/mnt/c/Users/emrea# docker images | grep my-app
    WARNING: This output is designed for human readability. For machine-readable output, please use --format.
    46.101.180.141:8083/my-app:1.0   e18236b5d15e        325MB         70.2MB   U
    my-app:1.0                       e18236b5d15e        325MB         70.2MB   U
```

#### Pushing the Image
Pushed the tagged image to Nexus:

```bash
    root@PC:/mnt/c/Users/emrea# docker push 46.101.180.141:8083/my-app:1.0
    The push refers to repository [46.101.180.141:8083/my-app]
    ...
    1.0: digest: sha256:e18236b5d15efc36509934d76863dc051371070b1b852dac07dec857822c596e size: 856
```

#### Checking with the REST API
Listed the components in the `docker-hosted` repository with the Nexus REST API. `my-app:1.0` is there:

```bash
    root@PC:/mnt/c/Users/emrea# curl -u emre:*** -X GET '46.101.180.141:8081/service/rest/v1/components?repository=docker-hosted'
    {
      "items" : [ {
        "id" : "ZG9ja2VyLWhvc3RlZDo0ZjFiYmNkZA",
        "repository" : "docker-hosted",
        "format" : "docker",
        "group" : "",
        "name" : "my-app",
        "version" : "1.0",
        "assets" : [ {
          "downloadUrl" : "http://46.101.180.141:8081/repository/docker-hosted/v2/my-app/manifests/1.0",
          "path" : "/v2/my-app/manifests/1.0",
          "id" : "ZG9ja2VyLWhvc3RlZDphMmEwMTBmMw",
          "repository" : "docker-hosted",
          "format" : "docker",
          "checksum" : {
            "sha256" : "e18236b5d15efc36509934d76863dc051371070b1b852dac07dec857822c596e",
            "sha1" : "ee76f1c7bcaa1c779b15fc8c0f9ecbb45ee2f7a1"
          },
          "contentType" : "application/vnd.oci.image.index.v1+json",
          "lastModified" : "2026-03-31T07:21:38.547+00:00",
          "lastDownloaded" : null,
          "uploader" : "emre",
          "uploaderIp" : "<my-ip>",
          "fileSize" : 856,
          "blobCreated" : "2026-03-31T07:21:38.549+00:00",
          "blobStoreName" : "mystore",
          "docker" : { }
        } ]
      } ],
      "continuationToken" : null
    }
```

#### Checking in the Browser
The image in the Nexus UI:

<img width="1788" height="1101" alt="image" src="https://github.com/user-attachments/assets/627f9d82-5902-4f9b-91dd-88691253dfb2" />

#### Command Summary

* `docker login <host:port>`: log in to a registry.
* `docker tag <source> <target>`: give an image a new name, e.g. with the registry address in front so it can be pushed there.
