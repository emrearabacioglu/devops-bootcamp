# Install Jenkins on DigitalOcean

**Technologies:** Jenkins, Docker, DigitalOcean, Linux

I created an Ubuntu Droplet on DigitalOcean, installed Docker on it and ran Jenkins as a Docker container.

## Summary
1. Created an Ubuntu Droplet, installed Docker and opened port 8080 (Jenkins UI) in the firewall.
2. Started Jenkins as a container:
   ```bash
   docker run -p 8080:8080 -p 50000:50000 -d \
     -v jenkins_home:/var/jenkins_home \
     -v /var/run/docker.sock:/var/run/docker.sock \
     jenkins/jenkins:lts
   ```
   The `jenkins_home` volume keeps jobs, plugins and settings when the container is recreated. Mounting `docker.sock` lets Jenkins use the Docker daemon of the server (needed for the next demos).
3. Initialized Jenkins: opened `http://<droplet-ip>:8080`, got the first admin password from the container and installed the suggested plugins.
   ```bash
   docker exec -it <container-id> bash
   cat /var/jenkins_home/secrets/initialAdminPassword
   ```
4. Made Docker commands available inside the Jenkins container (as root):
   ```bash
   docker exec -it -u 0 <container-id> bash
   curl https://get.docker.com/ > dockerinstall && chmod 777 dockerinstall && ./dockerinstall
   chmod 666 /var/run/docker.sock
   ```

## Result
Jenkins was running on the Droplet, reachable on port 8080, and was initialized with the suggested plugins. This setup is used by the other projects in this module.
