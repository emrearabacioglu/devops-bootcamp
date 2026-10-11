# Create a Jenkins Shared Library

**Technologies:** Jenkins, Groovy, Docker, Git, Java, Maven

I moved the build and Docker steps of the Java Maven pipeline into a Jenkins Shared Library and used it from `java-maven-app/Jenkinsfile`.

## Summary
1. Created a separate Git repo for the library: [jenkins-shared-library](https://github.com/emrearabacioglu/jenkins-shared-library).
2. Added the functions there:
   - `vars/buildJar.groovy` runs `mvn package` and prints the branch name from `$GIT_BRANCH`
   - `vars/buildImage.groovy`, `vars/dockerLogin.groovy`, `vars/dockerPush.groovy` call the `Docker` class
   - `src/com/example/Docker.groovy` is the class with `buildDockerImage`, `dockerLogin` (uses the `docker-hub-repo` credentials) and `dockerPush`
3. Used the library globally: *Manage Jenkins → System → Global Pipeline Libraries* (name `jenkins-shared-library`, my GitHub repo), then `@Library('jenkins-shared-library')` in the Jenkinsfile.
4. Final version, only for this project: `java-maven-app/Jenkinsfile` loads the library directly with `library identifier: 'jenkins-shared-library@master', retriever: modernSCM(...)` and the `github-credentials`.
5. The pipeline now only calls `buildJar()`, `buildImage 'emrearabacioglu/demo-app:jma-3.0'`, `dockerLogin()` and `dockerPush 'emrearabacioglu/demo-app:jma-3.0'`. The deploy stage still uses `java-maven-app/script.groovy`.

## Result
Jenkins loads the library from GitHub, builds the jar and pushes the `jma-3.0` image:
```
Loading library jenkins-shared-library@master
...
Checking out Revision 5d73a3e1ca7d6e3a1f0246abb0c83e847e08ac1d (master)
...
building the application.. for branch jenkins-shared-lib
...
[INFO] BUILD SUCCESS
...
+ docker build -t emrearabacioglu/demo-app:jma-3.0 .
...
+ docker login -u emrearabacioglu --password-stdin
Login Succeeded
...
+ docker push emrearabacioglu/demo-app:jma-3.0
The push refers to repository [docker.io/emrearabacioglu/demo-app]
jma-3.0: digest: sha256:3c815248c19e549f5f3a04844d7bb86614a8de79d2965be158e84003c6aa6c17 size: 1159
Finished: SUCCESS
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
