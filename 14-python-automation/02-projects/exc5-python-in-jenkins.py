"""
EXERCISE 5: Python in Jenkins Pipeline
Create a Jenkins job that fetches all the available images from your application's ECR repository using Python. It allows the user to select the image from the list through user input and deploys the selected image to the EC2 server using Python.

Instructions

Do the following preparation:

Start EC2 instance and install Docker on it
Install Python, Pip and all needed Python dependencies in Jenkins
Create 3 Docker images with tags 1.0, 2.0, 3.0 from one of the previous projects


Once all the above is configured, create a Jenkins Pipeline with the following steps:

Fetch all 3 images from the ECR repository (using Python)
Let the user select the image from the list (hint: https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/)
SSH into the EC2 server (using Python)
Run docker login to authenticate with ECR repository (using Python)
Start the container from the selected image from step 2 on EC2 instance (using Python)
Validate that the application was successfully started and is accessible by sending a request to the application (using Python)
"""
