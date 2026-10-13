# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Run Nexus on Droplet and Publish Artifact to Nexus

### Demo Executed: Install and Run Nexus on a Cloud Server

#### Setup
Set up a cloud server for Sonatype Nexus and ran it with its own user instead of root.

- Installed OpenJDK 17, because Nexus needs Java.
- Downloaded the Nexus archive to `/opt` and extracted it.
- Created a `nexus` user and group, and gave it ownership of the Nexus app directory and the data directory (`sonatype-work`), so Nexus doesn't run as `root`.
- Switched to the `nexus` user and started Nexus in the background.
- Checked the process and that it listens on the default port `8081`, and opened the port in the firewall.
- Got the generated initial admin password from the server to log in to the Nexus web UI.

#### Commands
All commands used in this part:

```bash
# Install Java
apt install openjdk-17-jre-headless

# Download and extract Nexus
cd /opt
wget https://download.sonatype.com/nexus/3/nexus-3.90.2-06-linux-x86_64.tar.gz
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

### Demo Executed: Publishing Artifacts to Nexus Repository

Published artifacts to the Nexus `maven-snapshots` repository with Gradle and with Maven. Each build tool needs the Nexus URL and credentials.

#### Gradle Project

##### Configuring `build.gradle`
Applied the `maven-publish` plugin and added the Nexus repository (URL, `allowInsecureProtocol` for http, credentials) to `build.gradle`:

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

##### Publish
Ran the publish task from the project root:

```bash
gradle publish
```

#### Maven Project

##### Configuring `pom.xml`
Added `maven-deploy-plugin` and set the Nexus repository URL and ID under `distributionManagement`:

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

##### Credentials in `settings.xml`
Maven reads the credentials from the user's local settings, not from the project. The `<id>` must be the same as in `pom.xml`.

Opened the settings file:

```bash
cd ~/.m2/
vim settings.xml
```

Added the server credentials:

```xml
<settings>
    <servers>
        <server>
            <id>nexus-snapshots</id>
            <username>emre</username>
            <password>***</password>
        </server>
    </servers>
</settings>
```

##### Package and Deploy
Went back to the project, built the jar and uploaded it to Nexus:

```bash
cd ~/IdeaProjects/java-maven-app/

# Compiles the code and builds the .jar artifact in the target/ directory
mvn package

# Uploads the built artifact and pom files to the Nexus repository
mvn deploy
```

<img width="998" height="1125" alt="image" src="https://github.com/user-attachments/assets/606e7c41-7f5f-4a16-b02b-98a34d464281" />
