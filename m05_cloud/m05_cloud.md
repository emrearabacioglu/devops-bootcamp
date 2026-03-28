# Cloud & Infrastructure as Service Basics with DigitalOcean

## Setup Server on DigitalOcean
In this section, a remote cloud server was provisioned and secured to prepare the deployment environment.

* **Droplet Provisioning:** Created an Ubuntu-based virtual machine on DigitalOcean.
* **Secure Access:** Generated an SSH key pair locally to establish a highly secure, passwordless connection to the server.
* **Firewall Configuration:** Configured Firewall to restrict inbound traffic, allowing only authorized SSH access on Port 22.
* **Remote Connection:** Connected to the remote server via terminal using the following command:

```  ssh root@<server_ip> ```

* **Install Java:** Installed Java in order to run the applications using following command:

``` apt install openjdk-17-jre-headless ```

## Deploy and run application artifact on Server

In this phase, the application was built locally and the resulting artifact was securely transferred and deployed to the remote cloud server for execution.

* **Artifact Generation:** Built the application locally from the cloned repository to generate the standalone `.jar` artifact.

  
  ```bash
   $ gradle build
  Starting a Gradle Daemon (subsequent builds will be faster)

  BUILD SUCCESSFUL in 9s
  7 actionable tasks: 7 up-to-date
  Consider enabling configuration cache to speed up this build: https://ds.gradle.org/9.4.0/userguide/configuration_cache_enabling.html ```

* **Secure File Transfer:** Transferred the generated artifact from the local machine directly to the remote server using the Secure Copy Protocol.
  ```bash
  $ scp build/libs/java-react-example.jar root@server-ip:/root
  java-react-example.jar                                                                17% 3570KB 466.7KB/s   00:36 ETA
  java-react-example.jar                                                            100%   20MB   1.3MB/s   00:1```

* **Application Execution:** Established an SSH connection to the remote server and executed the packaged application.
  ```bash
    root@ubuntu-droplet:~# ls
  java-react-example.jar
  root@ubuntu-droplet:~# java -jar java-react-example.jar
  
    .   ____          _            __ _ _
   /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
  ( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
   \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
    '  |____| .__|_| |_|_| |_\__, | / / / /
   =========|_|==============|___/=/_/_/_/
  
   :: Spring Boot ::                (v3.5.5)
  
  2026-03-28T09:29:08.117Z  INFO 3129 --- [           main] com.coditorium.sandbox.Application       : Starting Application using Java 17.0.18 with PID 3129 (/root/java-react-example.jar started by root in /root)
  2026-03-28T09:29:08.136Z  INFO 3129 --- [           main] com.coditorium.sandbox.Application       : No active profile set, falling back to 1 default profile: "default"
  2026-03-28T09:29:08.525Z  INFO 3129 --- [           main] .e.DevToolsPropertyDefaultsPostProcessor : For additional web related logging consider setting the 'logging.level.web' property to 'DEBUG'
  2026-03-28T09:29:14.554Z  INFO 3129 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port 7071 (http)
  2026-03-28T09:29:14.650Z  INFO 3129 --- [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
  2026-03-28T09:29:14.653Z  INFO 3129 --- [           main] o.apache.catalina.core.StandardEngine    : Starting Servlet engine: [Apache Tomcat/10.1.44]
  2026-03-28T09:29:15.338Z  INFO 3129 --- [           main] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring embedded WebApplicationContext
  2026-03-28T09:29:15.346Z  INFO 3129 --- [           main] w.s.c.ServletWebServerApplicationContext : Root WebApplicationContext: initialization completed in 6809 ms
  2026-03-28T09:29:16.996Z  INFO 3129 --- [           main] o.s.b.a.w.s.WelcomePageHandlerMapping    : Adding welcome page: class path resource [static/index.html]
  2026-03-28T09:29:18.681Z  INFO 3129 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 7071 (http) with context path '/'
  2026-03-28T09:29:18.777Z  INFO 3129 --- [           main] com.coditorium.sandbox.Application       : Started Application in 14.315 seconds (process running for 17.004)

  ```

* **Firewall Configuration:** Configured Firewall to restrict inbound traffic, allowing only authorized public access on Port 7071.

* **Verification:** Successfully accessed and validated the live application through a web browser using the server's public IP address and the port 7071.
```bash
  root@ubuntu-droplet:~# ps aux | grep java
  root        3296 18.7 28.1 2228256 132188 pts/0  Sl   09:35   0:15 java -jar java-react-example.jar
  root        3330  0.0  0.4   7076  2048 pts/0    S+   09:37   0:00 grep --color=auto java
  root@ubuntu-droplet:~# netstat -lpnt
  Active Internet connections (only servers)
  Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
  tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      1/init
  tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      669/systemd-resolve
  tcp        0      0 127.0.0.54:53           0.0.0.0:*               LISTEN      669/systemd-resolve
  tcp6       0      0 :::7071                 :::*                    LISTEN      3296/java
  tcp6       0      0 :::22                   :::*                    LISTEN      1/init
  root@ubuntu-droplet:~#
```

## Create and configure a Linux user on a cloud server
To enhance security and avoid using the root account for daily operations, a dedicated user was created and configured with administrative privileges and SSH key-based authentication.

* **User Creation:** Created a new standard user (`emre`) along with a dedicated home directory.
* **Privilege Escalation:** Added the new user to the `sudo` group to allow execution of administrative commands when necessary.
* **User Context Switch:** Switched the terminal session from the `root` user to the newly created user profile.
* **SSH Configuration:** Created a `.ssh` directory and opened the `authorized_keys` file to store the public SSH key for secure, passwordless remote access.

### Commands used in this section:
```bash
adduser emre
usermod -aG sudo emre
su - emre
mkdir .ssh
sudo vim .ssh/authorized_keys
```
