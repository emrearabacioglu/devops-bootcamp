### Exercises for Module "Container Orchestration with Kubernetes"

**Business Case:**Your company’s java-mysql application is running with docker-compose on a server. This application is used often internally and by your company clients too. You noticed that the server isn't very stable: Often a database container dies or the application itself, or docker daemon must be restarted. During this time people can't access the app!

So when this happens, the users write to you to tell you that the app is down and ask you to fix it. You SSH into the server, restart the containers with docker-compose and containers start again.

But this is annoying work, plus it doesn't look good for your company that your clients often can't access the app. So you want to make your application more reliable and highly available. You want to replicate both the database and the app, so if one container goes down, there is always a backup. Also you don't want to rely on a single server, but have multiple, in case 1 whole server goes down or gets rebooted etc.



So you look into different solutions and decide to use the container orchestration tool Kubernetes to solve the issue. For now you want to configure it and deploy your application manually, since it's a new tool and want to try it out manually before automating.

******

<details>
<summary>EXERCISE 1: Create a Kubernetes cluster</summary>
 <br />
  
 **Objectives:**
 
* Create a Kubernetes cluster (Minikube or LKE)

↳ **Execution:**


</details>

******

<details>
<summary>EXERCISE 2: Deploy Mysql with 2 replicas</summary>
 <br />
  
 **Objectives:**
 
* Deploy Mysql database with 2 replicas and volumes for data persistence

↳ **Execution:**


</details>

******

<details>
<summary>EXERCISE 3: Deploy your Java Application with 2 replicas</summary>
 <br />
  
 **Objectives:**
 
* Deploy the Java application with 2 replicas - note: once you have pushed your image to docker hub, you will need to ensure you are using this image name and tag in your application's configuration

↳ **Execution:**


  With docker-compose, you were setting env_vars on the server. In K8s there are separate components for that, so you want to:

* Create ConfigMap and Secret with the correct values and reference them in the application deployment config file.

↳ **Execution:**


</details>

******

<details>
<summary>EXERCISE 4: Deploy phpmyadmin</summary>
 <br />
  
 **Objectives:**
 
* Deploy phpmyadmin to access Mysql UI.
For this deployment you just need 1 replica, since this is only for your own use, so it doesn't have to be Highly Available. A simple deployment.yaml file and internal service will be enough.
↳ **Execution:**


</details>

******

Now your application setup is running in the cluster, but you still need a proper way to access the application. Also, you don't want users to access the application using the IP address but instead to use a domain name. For that, you want to install Ingress controller in the cluster and configure ingress access for your application.


******

<details>
<summary>EXERCISE 5: Deploy Ingress Controller</summary>
 <br />
  
 **Objectives:**
 
* Deploy Ingress Controller in the cluster - using Helm

↳ **Execution:**


</details>

******

<details>
<summary>EXERCISE 6: Create Ingress rule</summary>
 <br />
  
 **Objectives:**
 
* Create an Ingress rule for your application’s access
  If you are using Minikube, the application must be accessible on my-java-app.com
  For LKE, use the Linode node-balancer address - line 48 of the Index.html file for the application must be updated to include the address

↳ **Execution:**


</details>

******

<details>
<summary>EXERCISE 7: Port-forward for phpmyadmin</summary>
 <br />

  However, you don't want to expose phpmyadmin for security reasons. So you configure port-forwarding for the service to access on localhost, whenever you need it.

 **Objectives:**
 
* Configure port-forwarding for phpmyadmin

↳ **Execution:**


</details>

******

<details>
<summary>EXERCISE 8: Create Helm Chart for Java App</summary>
 <br />

  As the final step, you decide to create a helm chart for your Java application where all the configuration files are configurable. You can then tell developers how they can use it by setting all the chart values. This chart will be hosted in its own git repository.
  
 **Objectives:**
 
* All config files: service, deployment, ingress, configMap, secret, will be part of the chart

↳ **Execution:**

* Create custom values file as an example for developers to use when deploying the application

↳ **Execution:**

* Deploy the java application using the chart with helmfile

↳ **Execution:**

* Host the chart in its own git repository

↳ **Execution:**


</details>

******
