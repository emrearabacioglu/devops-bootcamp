# CD - Deploy to EKS cluster from Jenkins Pipeline

**Technologies:** Kubernetes, Jenkins, AWS EKS, Docker, Linux

I connected my Jenkins server (a Docker container on a DigitalOcean droplet) to the EKS cluster `demo-cluster` from the eksctl demo, and a pipeline deployed nginx to it with `kubectl`.

## Summary
1. Opened a root shell in the Jenkins container (`docker exec -u 0`) and installed `kubectl` and `aws-iam-authenticator` into `/usr/local/bin`.
2. Wrote a kubeconfig for the cluster (`kubeconfig/config`, certificate data replaced with `***`). It has the EKS endpoint and uses `aws-iam-authenticator` to get a token for `demo-cluster`.
3. Created `.kube` in the Jenkins home as the jenkins user and copied the file there with `docker cp config <container>:/var/jenkins_home/.kube/`.
4. Added the AWS access key ID and secret key as Jenkins credentials: `jenkins_aws_access_key_id` and `jenkins_aws_access_secret_key`.
5. In `java-maven-app/Jenkinsfile` the deploy stage loads them as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` and runs `kubectl create deployment nginx-deployment --image=nginx`. The build stages only print a message in this demo.

## Result
The deploy stage creates the deployment and the build finishes. The pod shows up on the cluster (still `Pending` when I checked):
```
Started by user emre
...
Masking supported pattern matches of $AWS_ACCESS_KEY_ID or $AWS_SECRET_ACCESS_KEY
...
deploying docker image...
+ kubectl create deployment nginx-deployment --image=nginx
deployment.apps/nginx-deployment created
...
Finished: SUCCESS

root@PC:/mnt/c/Users/emrea# kubectl get pod
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-7d6869886d-bvbm6   0/1     Pending   0          4m52s
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
