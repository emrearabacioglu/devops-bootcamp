# Run Nexus on Droplet and Publish Artifact to Nexus

**Technologies:** Nexus, DigitalOcean, Linux, Java, Gradle, Maven

I installed Nexus on a DigitalOcean Droplet, created a Nexus user for uploads and published jar files from a Gradle project and a Maven project to the `maven-snapshots` repository.

## Summary
1. On the Droplet I installed Java (`openjdk-17-jre-headless`), downloaded `nexus-3.90.2-06` to `/opt` and extracted it.
2. Created a `nexus` Linux user, gave it ownership of `nexus-3.90.2-06` and `sonatype-work/`, and started Nexus as that user with `/opt/nexus-3.90.2-06/bin/nexus start`, so it doesn't run as root.
3. Checked the process and port 8081 with `ps aux` and `netstat -lnpt`, opened 8081 in the firewall and logged in to the UI with the password from `/opt/sonatype-work/nexus3/admin.password`.
4. In the Nexus UI I created a user `emre` and a role that can upload to `maven-snapshots`, instead of using the admin account.
5. Gradle (`java-gradle-app/`): `build.gradle` applies the `maven-publish` plugin and points to `http://46.101.180.141:8081/repository/maven-snapshots/` with `allowInsecureProtocol = true`. The credentials come from `gradle.properties` (`repoUser`, `repoPassword`).
6. Maven (`java-maven-app/`): `pom.xml` has the `maven-deploy-plugin` and a `distributionManagement` block with the id `nexus-snapshots`. Maven reads the credentials for that id from `~/.m2/settings.xml` (username `emre`, password `***`).

## Run
```bash
# in java-gradle-app/
gradle build
gradle publish

# in java-maven-app/
mvn package
mvn deploy
```

## Result
After both uploads I checked the `maven-snapshots` repository in the Nexus UI and saw both artifacts.

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
