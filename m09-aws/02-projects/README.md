### Exercises for Module "AWS Services"

**Business Case:** Your company has decided that they will use AWS as a cloud provider to deploy their applications. It's too much overhead to manage multiple platforms, including the billing etc.

So you need to deploy the previous NodeJS application on an EC2 instance now. This means you need to create and prepare an EC2 server with the AWS Command Line Tool to run your NodeJS app container on it.







******

<details>
<summary>EXERCISE 1: Create IAM user</summary>
 <br />
 
**Case:** You need an IAM user with correct permissions to execute the tasks below.
 
**Objectives:**
* Create a new IAM user using "your name" as a username and "devops" as the user-group
* Give the "devops" group all needed permissions to execute the tasks below - with login and CLI credentials
* Note: Do that using the AWS UI with Admin User



</details>

******

<details>
<summary>EXERCISE 2: Configure AWS CLI</summary>

 <br />
 
**Case:** You want to use the AWS CLI for the following tasks. So, to be able to interact with the AWS account from the AWS Command Line tool you need to configure it correctly.
 
**Objectives:**
* Set credentials for that user for AWS CLI
* Configure correct region for your AWS CLI


</details>

******

<details>
<summary>EXERCISE 3: Create VPC</summary>
 <br />
 
**Case:** You want to create the EC2 Instance in a dedicated VPC, instead of using the default one. So, using the AWS CLI.

**Objectives:**

* Create a new VPC with 1 subnet
* Create a security group in the VPC that will allow you access on ssh port 22 and will allow browser access to your Node application


</details>

******

<details>
<summary>EXERCISE 4: Create EC2 Instance</summary>
 <br />

**Objectives:**

* Create an EC2 instance in that VPC with the security group you just created and ssh key file


</details>

******

<details>
<summary>EXERCISE 5: SSH into the server and install Docker on it</summary>
 <br />
 
**Case:** Once the EC2 instance is created successfully, you want to prepare the server to run Docker containers.
 
**Objectives:**

* SSH into the server
* Install Docker on it to run the dockerized application later

</details>

******

### Set up Continuous Deployment


**Business Case:** Now you don't want to deploy manually to the server all the time, because it's time-consuming and also sometimes you miss it, when changes are made and the new docker image is built by the pipeline. When you forget to check the pipeline, your team members need to write you and ask you to deploy the new version.

As a solution, you want to automate this thing to save you and your team members time and energy.



******

<details>
<summary>EXERCISE 6: Add docker-compose for deployment</summary>
 <br />

**Objectives:**

* Add docker-compose to your NodeJS application

This is because you want to have the whole configuration for starting the docker container in a file, in case you need to make change or add a database later, instead of a plain docker command with parameters.

Use repository: https://gitlab.com/twn-devops-bootcamp/latest/09-aws/aws-exercises


</details>

******

<details>
<summary>EXERCISE 7: Add "deploy to EC2" step to your existing pipeline</summary>
 <br />
 
 **Objectives:**
 
* Add a deployment step to the Jenkinsfile from the previous exercise’s project to deploy to EC2.


</details>

******

<details>
<summary>EXERCISE 8: Configure access from browser (EC2 Security Group)</summary>
 <br />
 
**Case:** After executing the Jenkins pipeline successfully, the application is deployed, but you still can't access it from the browser. You need to open the correct port on the server. For that, using the AWS CLI,

**Objectives:**

* Configure the EC2 security group to access your application from a browser


</details>

******

<details>
<summary>EXERCISE 9: Configure automatic triggering of multi-branch pipeline</summary>
 <br />

**Case:** Your team members are creating branches to add new features to the application or fix any issues, so you don't want to build and deploy these half-done features or bug fixes. You want to build and deploy only to the master branch. All other branches should only run tests. Add this logic to the Jenkinsfile:

**Objectives:**

* Add branch based logic to Jenkinsfile
* Add webhook to trigger pipeline automatically

</details>

