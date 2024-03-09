# ByteBracket-Utils
AWS Lambda functions and other utilities for ByteBracket.io, a better way to bracket.

Generic docker deployment instructions:

Enter the directory and login to your aws account:

`cd <PATH_TO_DIRECTORY_CONTAINING_DOCKERFILE>`

`aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com`

Build the docker image:

`docker build -t <NAME_OF_DOCKER_IMAGE> .`

If you have no repository, make one:

`aws ecr create-repository --repository-name <NAME_OF_ECR_RESPOSITORY> --region us-east-1 --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE`

Link the image to your ECR repo:

`docker tag  <NAME_OF_DOCKER_IMAGE>:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/<NAME_OF_ECR_RESPOSITORY>:latest`

Push the image to your ECR repo:

`docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/<NAME_OF_ECR_RESPOSITORY>:latest`