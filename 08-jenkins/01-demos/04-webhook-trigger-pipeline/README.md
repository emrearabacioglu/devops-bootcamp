# Configure Webhook to trigger CI Pipeline automatically on every change

**Technologies:** Jenkins, GitHub, Git, Docker, Java, Maven

Before this demo I had to click "Build Now" in Jenkins after every push. With a webhook, GitHub tells Jenkins about every push and the pipeline starts by itself. I used GitHub instead of GitLab.

I connected the webhook to the last pipeline of this module: the multibranch pipeline with dynamic versioning (`05-dynamic-versioning`). This setup uses only the Jenkins UI and the GitHub UI, so there is no code for it.

## Summary
1. Jenkins: *Manage Jenkins → Plugins → Available plugins* → installed **Multibranch Scan Webhook Trigger**.
2. Opened the multibranch job → *Configure* → *Scan Multibranch Pipeline Triggers*, checked **Scan by webhook**, entered a trigger token (for example `githubtoken`) and saved. The plugin gives this URL for the job:
   ```
   http://<jenkins-server-ip>:8080/multibranch-webhook-trigger/invoke?token=<trigger-token>
   ```
3. GitHub: opened the app repository → *Settings → Webhooks → Add webhook*.
   - **Payload URL:** the URL above
   - **Content type:** `application/json`
   - **Which events:** "Just the push event"
4. Clicked *Add webhook*. GitHub sends a test ping, and the green tick in *Recent Deliveries* shows that Jenkins answered.
5. Jenkins must be reachable from the internet on port 8080 (Droplet firewall), otherwise GitHub cannot call it.

## Result
After a `git push`, Jenkins scans the repository and starts the pipeline for the changed branch.

The pipeline itself also pushes a commit (the version bump). Without a fix this would start the pipeline again and again, so the job ignores commits made by the Jenkins user (see `05-dynamic-versioning`).
