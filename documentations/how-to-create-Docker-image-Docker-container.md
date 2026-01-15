Run these command in terminal to create docker image using the dockerfile.

> ! Make sure to be in the same working directory as the dockerfile

# Pre-check
Check if the latest version of `inv_mgmt_playbook` will be copied to docker image.

1. Open Dockerfile
2. Check the line `COPY ./inv_mgmt_playbook_v4 /inv_mgmt_playbook`
3. Update the `_v` based on the latest version available

Check and change the Timezone for your Docker image

1. Open Dockerfile
2. Check the line # Change date and time
3. Hash out the non required timezone

# Step 1: Create Docker Image from Dockerfile
```sh
# For ARM based architechture
docker buildx build --platform linux/arm64 -t jpc1-mgmt:v.1 .
# For AMD based architechture
docker buildx build --platform linux/amd64 -t jpc1-mgmt:v.1 .
```

# Step 2: Create Docker container na
Run this command to create a new docker container using the docker image created in the above. 

> Replace "container-name" with desired name for your container

```sh
docker run -it --name container-name jpc1-mgmt:v.1
```