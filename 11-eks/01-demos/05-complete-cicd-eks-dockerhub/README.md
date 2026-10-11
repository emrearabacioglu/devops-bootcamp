# Complete CI/CD Pipeline with EKS and private DockerHub registry

**Technologies:** Kubernetes, Jenkins, AWS EKS, Docker Hub, Java, Maven, Linux, Docker, Git

I extended the Jenkins pipeline of the Java Maven app: it builds a new version, pushes the image to my private Docker Hub repo and deploys it to the EKS cluster.

## Summary
1. Installed `gettext-base` in the Jenkins container, because the deploy stage uses `envsubst` to fill in the variables in the manifests.
2. Created the `docker-registry` secret `my-registry-key` in the cluster with my Docker Hub login, so the nodes can pull the private `emrearabacioglu/demo-app` image. Deleted the nginx deployment from the previous demo.
3. Wrote `java-maven-app/kubernetes/deployment.yaml` (2 replicas, `imagePullSecrets: my-registry-key`, image `emrearabacioglu/demo-app:$IMAGE_NAME`) and `java-maven-app/kubernetes/service.yaml` (ClusterIP, port 80 to 8080). `$APP_NAME` and `$IMAGE_NAME` are set in the pipeline.
4. `java-maven-app/Jenkinsfile` stages:
   - increment version with Maven, image tag is `<version>-<build number>`
   - build the jar with `mvn clean package`
   - build the image and push it to Docker Hub (credentials `docker-hub-repo`)
   - deploy: `envsubst < kubernetes/deployment.yaml | kubectl apply -f -` and the same for `service.yaml`, with the AWS keys from `jenkins_aws_access_key_id` / `jenkins_aws_access_secret_key`
   - commit the version bump and push it to the `jenkins-jobs` branch (credentials `github-credentials`)
5. At first one pod was `Pending` with `Too many pods`: the t2.micro nodes hit their pod limit. Once there was room, both replicas were running.

## Result
The pipeline deploys to EKS and pushes the version bump; both pods are running:
```
+ envsubst
+ kubectl apply -f -
deployment.apps/java-maven-app configured
...
+ git push origin HEAD:jenkins-jobs
To https://github.com/emrearabacioglu/java-maven-app.git
   321573d..6329e06  HEAD -> jenkins-jobs
...
Finished: SUCCESS

root@PC:~/k8s-on-aws# kubectl get pod
NAME                              READY   STATUS    RESTARTS   AGE
java-maven-app-646744859d-8wgxv   1/1     Running   0          9m58s
java-maven-app-646744859d-czzr6   1/1     Running   0          3m2s
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
