# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Create server and deploy application on DigitalOcean

### Demo Executed: Setup Server on DigitalOcean

#### Droplet and Access
- Created an Ubuntu droplet on DigitalOcean.
- Generated an SSH key pair locally for passwordless SSH login.
- Set up the firewall to allow only SSH (port 22) inbound.

Connected to the server:

```
ssh root@<server_ip>
```

#### Install Java
Installed Java to be able to run the application:

```
apt install openjdk-17-jre-headless
```

### Demo Executed: Deploy and run application artifact on Server

#### Build the Artifact
Built the `.jar` locally from the cloned repository with Gradle:

```bash
$ gradle build
Starting a Gradle Daemon (subsequent builds will be faster)

BUILD SUCCESSFUL in 9s
7 actionable tasks: 7 up-to-date
Consider enabling configuration cache to speed up this build: https://ds.gradle.org/9.4.0/userguide/configuration_cache_enabling.html
```

#### Copy the Artifact to the Server
Copied the jar to the droplet with `scp`:

```bash
$ scp build/libs/java-react-example.jar root@server-ip:/root
...
java-react-example.jar                                                            100%   20MB   1.3MB/s   00:1
```

#### Run the Application
Connected with SSH and started the jar. Tomcat starts on port 7071:

```bash
root@ubuntu-droplet:~# ls
java-react-example.jar
root@ubuntu-droplet:~# java -jar java-react-example.jar
...
2026-03-28T09:29:08.117Z  INFO 3129 --- [           main] com.coditorium.sandbox.Application       : Starting Application using Java 17.0.18 with PID 3129 (/root/java-react-example.jar started by root in /root)
...
2026-03-28T09:29:14.554Z  INFO 3129 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port 7071 (http)
...
2026-03-28T09:29:18.681Z  INFO 3129 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 7071 (http) with context path '/'
2026-03-28T09:29:18.777Z  INFO 3129 --- [           main] com.coditorium.sandbox.Application       : Started Application in 14.315 seconds (process running for 17.004)
```

#### Firewall and Check
Added a firewall rule to allow public access on port 7071. After that, the app opened in the browser at the server's public IP on port 7071.

The java process and port 7071 listening on the server:

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

### Demo Executed: Create and configure a Linux user on a cloud server

#### New User
Created a separate user so I don't use root for daily work:
- Created the user `emre` with a home directory.
- Added `emre` to the `sudo` group for admin commands.
- Switched from `root` to `emre`.
- Created `.ssh` and opened `authorized_keys` to add my public SSH key for passwordless login.

Commands used:

```bash
adduser emre
usermod -aG sudo emre
su - emre
mkdir .ssh
sudo vim .ssh/authorized_keys
```
