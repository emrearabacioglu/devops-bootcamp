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
   
# Publishing Artifacts to Nexus Repository

This document demonstrates how to publish build artifacts to a Nexus repository using both Gradle and Maven build tools. To do this, each build tool must be configured with the Nexus server address and authentication credentials.

## 1. Publishing a Gradle Project

### Configuring `build.gradle`
To publish a Java application using Gradle, the `maven-publish` plugin is applied, and the Nexus repository details (URL, security protocol, and credentials) are defined inside the `build.gradle` file.

```groovy
apply plugin: 'maven-publish'

publishing {
    publications {
        create("maven", MavenPublication) {
            artifact("build/libs/my-app-$version" + ".jar") {
                extension 'jar'
            }
        }
    }
    repositories {
        maven {
            name 'nexus'
            url "http://46.101.180.141:8081/repository/maven-snapshots/"
            allowInsecureProtocol = true
            credentials {
                username project.repoUser
                password project.repoPassword
            }
        }
    }
}
```

### Executing the Publish Command
Execute the publish task from the project root directory.

```bash
gradle publish
```

---

## 2. Publishing a Maven Project

### Configuring `pom.xml`
For a Maven-based application, the `maven-deploy-plugin` is required. The target Nexus repository URL and its specific ID are defined under the `distributionManagement` section in the `pom.xml` file.

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-deploy-plugin</artifactId>
    <version>3.1.4</version>
</plugin>

<distributionManagement>
    <snapshotRepository>
        <id>nexus-snapshots</id>
        <url>http://46.101.180.141:8081/repository/maven-snapshots/</url>
    </snapshotRepository>
</distributionManagement>
```

### Configuring Credentials in `settings.xml`
Maven securely reads server authentication details from the local user settings, rather than the project file. The credentials must be mapped to the exact `<id>` used in the `pom.xml`.

Navigate to the Maven configuration directory and edit the settings file:
```bash
cd ~/.m2/
vim settings.xml
```

Add the following configuration:
```xml
<settings>
    <servers>
        <server>
            <id>nexus-snapshots</id>
            <username>emre</username>
            <password>12345678</password>
        </server>
    </servers>
</settings>
```

### Packaging and Deploying
Navigate back to the project directory to compile, package the application into a `.jar` file, and deploy it to the remote Nexus repository.

```bash
cd ~/IdeaProjects/java-maven-app/

# Compiles the code and builds the .jar artifact in the target/ directory
mvn package

# Uploads the built artifact and pom files to the Nexus repository
mvn deploy
```
<img width="998" height="1125" alt="image" src="https://github.com/user-attachments/assets/606e7c41-7f5f-4a16-b02b-98a34d464281" />

   
## Nexus REST API
   
## Blob Store
   
## Component vs Asset 
   
## Cleanup Policies and Scheduled Tasks
