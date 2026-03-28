# Artifact Repository Manager with Nexus

   
## Install and Run Nexus on a Cloud Server

In this module, a remote cloud server was provisioned and configured to host the Sonatype Nexus Repository Manager. Security best practices were applied by creating a dedicated user for the service.

* **Java Installation:** Installed OpenJDK 17 Runtime Environment, as Nexus requires Java to run.
* **Download and Extraction:** Fetched the Nexus Repository Manager archive directly to the server's `/opt` directory and extracted it.
* **Security & Permissions:** Created a dedicated `nexus` user and group. Changed the ownership of the Nexus application and data directories (`sonatype-work`) to this new user to prevent the application from running with `root` privileges.
* **Service Execution:** Switched to the `nexus` user and started the Nexus service in the background.
* **Verification:** Verified the running process and ensured the service was actively listening on the default port `8081` configured the firewall accordingly.
* **Authentication:** Retrieved the auto-generated initial administrator password from the server to log into the Nexus Web UI.

```bash
# Install Java
apt install openjdk-17-jre-headless

# Download and extract Nexus
cd /opt
wget [https://download.sonatype.com/nexus/3/nexus-3.90.2-06-linux-x86_64.tar.gz](https://download.sonatype.com/nexus/3/nexus-3.90.2-06-linux-x86_64.tar.gz)
tar -zxvf nexus-3.90.2-06-linux-x86_64.tar.gz

# Create user and set permissions
adduser nexus
chown -R nexus:nexus nexus-3.90.2-06
chown -R nexus:nexus sonatype-work/

# Switch to nexus user and start the service
su - nexus
/opt/nexus-3.90.2-06/bin/nexus start

# Verify service and ports
ps aux | grep nexus
netstat -lnpt

# Retrieve initial admin password
cat /opt/sonatype-work/nexus3/admin.password
```
   
## Introduction to Nexus
   
## Repository Types
   
## Publish Artifact to Repository
   
## Nexus REST API
   
## Blob Store
   
## Component vs Asset 
   
## Cleanup Policies and Scheduled Tasks
