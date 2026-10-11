# Create server and deploy application on DigitalOcean

**Technologies:** DigitalOcean, Linux, Java, Gradle

I created an Ubuntu Droplet on DigitalOcean, built the Java Gradle app in `java-react-example/` on my machine and ran the jar on the server.

## Summary
1. Created an Ubuntu Droplet, added my SSH public key and a firewall rule that only allows SSH (port 22) from my IP.
2. Connected as root and installed Java with `apt install openjdk-17-jre-headless`.
3. Built the app locally with `gradle build` (build config in `java-react-example/build.gradle`) and copied `build/libs/java-react-example.jar` to the server with `scp`.
4. Started the app with `java -jar java-react-example.jar`. Spring Boot starts Tomcat on port 7071 (set in `java-react-example/src/main/resources/application.yml`).
5. Opened port 7071 in the firewall and opened the app in the browser on the server's public IP.
6. Created a new Linux user `emre`, added it to the `sudo` group and added my public key to `~/.ssh/authorized_keys`, so I don't work as root.

## Result
The app starts on the Droplet and the java process listens on port 7071:
```
2026-03-28T09:29:18.681Z  INFO 3129 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 7071 (http) with context path '/'
2026-03-28T09:29:18.777Z  INFO 3129 --- [           main] com.coditorium.sandbox.Application       : Started Application in 14.315 seconds (process running for 17.004)
...
root@ubuntu-droplet:~# ps aux | grep java
root        3296 18.7 28.1 2228256 132188 pts/0  Sl   09:35   0:15 java -jar java-react-example.jar
...
root@ubuntu-droplet:~# netstat -lpnt
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      1/init
...
tcp6       0      0 :::7071                 :::*                    LISTEN      3296/java
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
