******
<details>
<summary>EXERCISE 1: Install Nexus on a server</summary>
 <br />
  
* Already had a server that running nexus from the module demostrations.

</details>

******
<details>
<summary>EXERCISE 2: Create npm hosted repository</summary>
 <br />
For a Node application:

* Create a new npm hosted repository with a new blob store

</details>

******
<details>
<summary>EXERCISE 3: Create user for team 1</summary>
 <br />
  
* Create Nexus user for the project 1 team to have access to this npm repository

</details>

******
<details>
<summary>EXERCISE 4: Build and publish npm tar</summary>
 <br />
You want to test that the project 1 user has correct access configured:

* Build and publish a nodejs tar package to the npm repo

</details>

******
<details>
  
<summary>EXERCISE 5: Create maven hosted repository</summary>
 <br />
For a Java application:

* Create a new maven hosted repository

</details>

******
<details>
  
<summary>EXERCISE 6: Create user for team 2</summary>
 <br />
 
* Create a Nexus user for project 2 team to have access to this maven repository
  
</details>

******
<details>
<summary>EXERCISE 7: Build and publish jar file</summary>
 <br />
  
You want to test that the project 2 user has the correct access configured and also upload the first version. So:

* Build and publish the jar file to the new repository using the team 2 user.

</details>

******
<details>
<summary>EXERCISE 8: Download from Nexus and start application</summary>
 <br />
  
* Create new user for droplet server that has access to both repositories
* On a digital ocean droplet, using Nexus Rest API, fetch the download URL info for the latest NodeJS app artifact
* Execute a command to fetch the latest artifact itself with the download URL
* Run it on the server!

</details>

******
<details>
<summary>EXERCISE 9: Automate</summary>
 <br />
  
You decide to automate the fetching from Nexus and starting the application So you:

* Write a script that fetches the latest version from npm repository. Untar it and run on the server!
* Execute the script on the droplet

</details>

*******
