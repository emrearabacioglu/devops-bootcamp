# Complete CI/CD Pipeline with EKS and AWS ECR

**Technologies:** Kubernetes, Jenkins, AWS EKS, AWS ECR, Java, Maven, Linux, Docker, Git

Same pipeline as `05-complete-cicd-eks-dockerhub`, but the image goes to a private AWS ECR repository instead of Docker Hub, and EKS pulls it from there.

## Summary
1. Created the ECR repository `java-maven-app` in the AWS console.
2. Added ECR credentials in Jenkins (`ecr-credentials`, user `AWS`, password from `aws ecr get-login-password`).
3. Created a second registry secret in the cluster, `aws-registry-key`, for `731872836472.dkr.ecr.eu-central-1.amazonaws.com` (user `AWS`, password is the ECR token).
4. `java-maven-app/kubernetes/deployment.yaml` now uses `aws-registry-key` and the ECR image URL. `service.yaml` is unchanged.
5. In `java-maven-app/Jenkinsfile` I added `DOCKER_REPO_SERVER` and pointed `DOCKER_REPO` to ECR. The build image stage logs in to ECR with `ecr-credentials` and pushes there. Version bump, deploy with `envsubst` + `kubectl apply` and the version commit are the same as before.

## Result
The image is pushed to ECR, the app is deployed to EKS and the version bump is committed; both pods run the new image:
```
+ docker login -u AWS --password-stdin 731872836472.dkr.ecr.eu-central-1.amazonaws.com
Login Succeeded
+ docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/java-maven-app:1.1.14-6
...
1.1.14-6: digest: sha256:fd04029134d36686a798ba497135e16ed898d58cc3da2a94c123e94854b903b6 size: 1159
...
deployment.apps/java-maven-app created
...
   ef42f60..c1b158f  HEAD -> jenkins-jobs
...
Finished: SUCCESS

root@PC:~/k8s-on-aws# kubectl get pod
NAME                              READY   STATUS    RESTARTS   AGE
java-maven-app-f5bb74f54-2kxj5    1/1     Running   0          3m9s
java-maven-app-f5bb74f54-k4s7r    1/1     Running   0          3m9s
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
