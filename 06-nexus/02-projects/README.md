******
<details>
<summary>PROJECT 1: Install Nexus on a server</summary>
 <br />
  
* Already had a server that running nexus from the module demostrations.

</details>

******
<details>
<summary>PROJECT 2: Create npm hosted repository</summary>
 <br />
For a Node application:

* Create a new npm hosted repository with a new blob store

created the blob store:
<img width="1061" height="478" alt="image" src="https://github.com/user-attachments/assets/59001ca2-b50f-479d-af48-52ba64f14d40" />


created repository:

<img width="592" height="373" alt="image" src="https://github.com/user-attachments/assets/32368147-7db8-4ad6-82ad-ae81d00c24ca" />


</details>

******
<details>
<summary>PROJECT 3: Create user for team 1</summary>
 <br />
  
* Create Nexus user for the project 1 team to have access to this npm repository

  <img width="859" height="644" alt="image" src="https://github.com/user-attachments/assets/5ad7f897-6c74-41be-889c-51f1615aef70" />

  <img width="973" height="613" alt="image" src="https://github.com/user-attachments/assets/fefb23fd-8304-40fb-ab6d-941b1642e54d" />


</details>

******
<details>
<summary>PROJECT 4: Build and publish npm tar</summary>
 <br />
You want to test that the project 1 user has correct access configured:

* Build and publish a nodejs tar package to the npm repo

  Steps to build the packet from a local repo, login to Nexus repository and publish to package:

```sh
$ npm pack
npm warn gitignore-fallback No .npmignore file found, using .gitignore for file exclusion. Consider creating a .npmignore file to explicitly control published files.
npm warn gitignore-fallback No .npmignore file found, using .gitignore for file exclusion. Consider creating a .npmignore file to explicitly control published files.
npm notice
npm notice 📦  nodejs-app@1.0.0
npm notice Tarball Contents
npm notice 166B Dockerfile
npm notice 95B Readme.md
npm notice 608B app/server.js
npm notice 329B package.json
npm notice Tarball Details
npm notice name: nodejs-app
npm notice version: 1.0.0
npm notice filename: nodejs-app-1.0.0.tgz
npm notice package size: 797 B
npm notice unpacked size: 1.2 kB
npm notice shasum: db0f98139fca182e481bf5fb680ea04375214f25
npm notice integrity: sha512-EFEoBTnEVSqjW[...]eCjiuWzFEISqg==
npm notice total files: 4
npm notice
nodejs-app-1.0.0.tgz


$ npm login --registry=http://46.101.180.141:8081/repository/npm-repo/
npm notice Log in on http://46.101.180.141:8081/repository/npm-repo/
Username: user1
Password:
Logged in on http://46.101.180.141:8081/repository/npm-repo/.



$ npm publish --registry=http://46.101.180.141:8081/repository/npm-repo/ nodejs-app-1.0.0.tgz
npm notice
npm notice 📦  nodejs-app@1.0.0
npm notice Tarball Contents
npm notice 166B Dockerfile
npm notice 95B Readme.md
npm notice 608B app/server.js
npm notice 329B package.json
npm notice Tarball Details
npm notice name: nodejs-app
npm notice version: 1.0.0
npm notice filename: nodejs-app-1.0.0.tgz
npm notice package size: 797 B
npm notice unpacked size: 1.2 kB
npm notice shasum: db0f98139fca182e481bf5fb680ea04375214f25
npm notice integrity: sha512-EFEoBTnEVSqjW[...]eCjiuWzFEISqg==
npm notice total files: 4
npm notice
npm notice Publishing to http://46.101.180.141:8081/repository/npm-repo/ with tag latest and default access
+ nodejs-app@1.0.0

```
Pic from Nexus UI:

<img width="1016" height="218" alt="image" src="https://github.com/user-attachments/assets/670946ed-3754-4b10-bf5f-6d685ee43305" />



</details>

******
<details>
  
<summary>PROJECT 5: Create maven hosted repository</summary>
 <br />
For a Java application:

* Create a new maven hosted repository

  <img width="1186" height="379" alt="image" src="https://github.com/user-attachments/assets/1a6a04f8-59ba-4f1d-9dce-0f51db9d3d6d" />


</details>

******
<details>
  
<summary>PROJECT 6: Create user for team 2</summary>
 <br />
 
* Create a Nexus user for project 2 team to have access to this maven repository

  Team2 Role:

  <img width="783" height="844" alt="image" src="https://github.com/user-attachments/assets/828052bf-9834-430c-bd81-86e6c0fffdc3" />

  User2:

  <img width="973" height="729" alt="image" src="https://github.com/user-attachments/assets/ca858158-0042-4d64-99fd-9d2aaea5137e" />

</details>

******
<details>
<summary>PROJECT 7: Build and publish jar file</summary>
 <br />
  
You want to test that the project 2 user has the correct access configured and also upload the first version. So:

* Build and publish the jar file to the new repository using the team 2 user.
  
Steps:
```sh
vim build.gradle #to set the url in plugin correctly for the new repo

vim gradle.properties #to set the credentials for user2

gradle build

$ gradle publish

[Incubating] Problems report is available at: file:///C:/Users/emrea/IdeaProjects/java-app/build/reports/problems/problems-report.html

Deprecated Gradle features were used in this build, making it incompatible with Gradle 10.

You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.

For more on this, please refer to https://docs.gradle.org/9.4.0/userguide/command_line_interface.html#sec:command_line_warnings in the Gradle documentation.

BUILD SUCCESSFUL in 19s
2 actionable tasks: 2 executed

```
Snapshot from the Neexus UI:

<img width="686" height="570" alt="image" src="https://github.com/user-attachments/assets/7cd58cab-260b-4e21-9343-9fa23bc915b0" />


</details>

******
<details>
<summary>PROJECT 8: Download from Nexus and start application</summary>
 <br />
  
* Create new user for droplet server that has access to both repositories
* On a digital ocean droplet, using Nexus Rest API, fetch the download URL info for the latest NodeJS app artifact
* Execute a command to fetch the latest artifact itself with the download URL
* Run it on the server!

New User: 

<img width="1015" height="745" alt="image" src="https://github.com/user-attachments/assets/030e898e-a26a-4dc8-982e-d6d3c2d78a7c" />

Steps on the Terminal: 

```bash
curl -u user3:12345678 -X GET 'http://46.101.180.141:8081/service/rest/v1/components?repository=npm-repo&sort=version'

wget --user=user3 --password=12345678 http://46.101.180.141:8081/repository/npm-repo/nodejs-app/-/nodejs-app-1.0.0.tgz

npm install

root@ubuntu-nexus:~/package# node app/server.js
{"level":30,"time":"2026-03-29T15:17:43.332Z","pid":35750,"hostname":"ubuntu-nexus","msg":"hello elastic world"}
{"level":30,"time":"2026-03-29T15:17:43.333Z","pid":35750,"hostname":"ubuntu-nexus","msg":"This is some great stuff"}
{"level":30,"time":"2026-03-29T15:17:43.333Z","pid":35750,"hostname":"ubuntu-nexus","msg":"Some more entries for our logging"}
{"level":30,"time":"2026-03-29T15:17:43.333Z","pid":35750,"hostname":"ubuntu-nexus","msg":"another line"}
{"level":30,"time":"2026-03-29T15:17:43.333Z","pid":35750,"hostname":"ubuntu-nexus","msg":"This never stops"}
{"level":30,"time":"2026-03-29T15:17:43.333Z","pid":35750,"hostname":"ubuntu-nexus","msg":"Logging logging all the way"}
{"level":30,"time":"2026-03-29T15:17:43.333Z","pid":35750,"hostname":"ubuntu-nexus","msg":"I think this is enough"}
{"level":30,"time":"2026-03-29T15:17:43.333Z","pid":35750,"hostname":"ubuntu-nexus","msg":"nope, one more!"}
{"level":30,"time":"2026-03-29T15:17:43.343Z","pid":35750,"hostname":"ubuntu-nexus","msg":"app listening on port 3000!"}


```



</details>

******
<details>
<summary>PROJECT 9: Automate</summary>
 <br />
  
You decide to automate the fetching from Nexus and starting the application So you:

* Write a script that fetches the latest version from npm repository. Untar it and run on the server!
* Execute the script on the droplet

Script: 
```bash
#!/bin/bash


DOWNLOAD_URL=$(curl -s -u user3:12345678 -X GET 'http://46.101.180.141:8081/service/rest/v1/search/assets?repository=maven-repo&name=my-app&sort=version' | jq -r '.items[0].downloadUrl')

wget --user=user3 --password=12345678 -O app.jar "$DOWNLOAD_URL"

java -jar app.jar

```
Execution: 

<img width="1320" height="409" alt="image" src="https://github.com/user-attachments/assets/0a5f1602-3258-4b43-807d-16b935bc14e5" />


</details>

*******
