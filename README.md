# DSAC_ASR_BACKEND

Core code required to run the serverless backend for DSAC South African speech recognition platform.

## Description

This codebase contains only the core code and logic that is required to host the ASR engine. Any sensitive Saigen IP is redacted in this version.

## Getting Started

### Dependencies

* An AWS account
* aws-cli
* Docker
* Python
* Prerequisite knowledge about docker containers and the AWS stack
* AWS IAM roles with the following permissions

### Installing

For Debian/Ubuntu:
* After creating an aws account install the aws-cli
```
sudo apt-get install aws
```
* Install Docker
```
sudo apt-get install docker.io
```
* Clone this repo
```
git clone https://github.com/arnold-saigen/DSAC_ASR_Backend.git
```

### Building and publishing container

* Go to docker context and build the container
```
>> cd ./DSAC_ASR_BACKEND/docker_context
>> sudo docker build -t dsac_asr_backend ./
```
* After building he image, upload the docker image to ECR
```
>> aws ecr get-login-password --region <your region> | sudo docker login --username AWS --password-stdin <your aws account ID>.dkr.ecr.<your region>.amazonaws.com
>> sudo docker tag dsac_asr_backend:latest <your aws account ID>.dkr.ecr.<your region>.amazonaws.com/dsac_asr_backend:latest
>> sudo docker push <your aws account ID>.dkr.ecr.<your region>.amazonaws.com/dsac_asr_backend:latest
```

### Setting up an elastic file system to host your models
You will need to create a 

### Setting up AWS ECS and Fargate

* Create a ECS Fargate cluster
```
>> aws ecs create-cluster --cluster-name fargate-cluster
```
* Register a task definition
```
{
  "ipcMode": null,
  "executionRoleArn": "arn:aws:iam::<your aws account ID>:role/<your aws IAM role>",
  "containerDefinitions": [
    {
      "dnsSearchDomains": null,
      "environmentFiles": null,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/<your task name>",
          "awslogs-region": "<your aws region>",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "entryPoint": null,
      "portMappings": [
        {
          "hostPort": 8000,
          "protocol": "tcp",
          "containerPort": 8000
        },
        {
          "hostPort": 2049,
          "protocol": "tcp",
          "containerPort": 2049
        }
      ],
      "command": null,
      "linuxParameters": null,
      "cpu": 0,
      "environment": [],
      "ulimits": null,
      "dnsServers": null,
      "mountPoints": [
        {
          "readOnly": null,
          "containerPath": "/root/models",
          "sourceVolume": "<your EFS name>"
        }
      ],
      "workingDirectory": null,
      "secrets": null,
      "dockerSecurityOptions": null,
      "memory": null,
      "memoryReservation": null,
      "volumesFrom": [],
      "stopTimeout": null,
      "image": "<your aws account ID>.dkr.ecr.<your aws region>.amazonaws.com/<your image name>:latest",
      "startTimeout": null,
      "firelensConfiguration": null,
      "dependsOn": null,
      "disableNetworking": null,
      "interactive": null,
      "healthCheck": null,
      "essential": true,
      "links": null,
      "hostname": null,
      "extraHosts": null,
      "pseudoTerminal": null,
      "user": null,
      "readonlyRootFilesystem": null,
      "dockerLabels": null,
      "systemControls": null,
      "privileged": null,
      "name": "<your task name>"
    }
  ],
  "placementConstraints": [],
  "memory": "8192",
  "taskRoleArn": "arn:aws:iam::<your aws account ID>:role/<your aws IAM role>",
  "compatibilities": [
    "EC2",
    "FARGATE"
  ],
  "taskDefinitionArn": "arn:aws:ecs:<your aws region>:<your aws account ID>:task-definition/<your task name>:1",
  "family": "<your task name>",
  "requiresAttributes": [
    {
      "targetId": null,
      "targetType": null,
      "value": null,
      "name": "com.amazonaws.ecs.capability.logging-driver.awslogs"
    },
    {
      "targetId": null,
      "targetType": null,
      "value": null,
      "name": "ecs.capability.execution-role-awslogs"
    },
    {
      "targetId": null,
      "targetType": null,
      "value": null,
      "name": "ecs.capability.efsAuth"
    },
    {
      "targetId": null,
      "targetType": null,
      "value": null,
      "name": "com.amazonaws.ecs.capability.ecr-auth"
    },
    {
      "targetId": null,
      "targetType": null,
      "value": null,
      "name": "com.amazonaws.ecs.capability.docker-remote-api.1.19"
    },
    {
      "targetId": null,
      "targetType": null,
      "value": null,
      "name": "ecs.capability.efs"
    },
    {
      "targetId": null,
      "targetType": null,
      "value": null,
      "name": "com.amazonaws.ecs.capability.task-iam-role"
    },
    {
      "targetId": null,
      "targetType": null,
      "value": null,
      "name": "com.amazonaws.ecs.capability.docker-remote-api.1.25"
    },
    {
      "targetId": null,
      "targetType": null,
      "value": null,
      "name": "ecs.capability.execution-role-ecr-pull"
    },
    {
      "targetId": null,
      "targetType": null,
      "value": null,
      "name": "com.amazonaws.ecs.capability.docker-remote-api.1.18"
    },
    {
      "targetId": null,
      "targetType": null,
      "value": null,
      "name": "ecs.capability.task-eni"
    }
  ],
  "pidMode": null,
  "requiresCompatibilities": [
    "FARGATE"
  ],
  "networkMode": "awsvpc",
  "cpu": "4096",
  "revision": 1,
  "status": "ACTIVE",
  "inferenceAccelerators": null,
  "proxyConfiguration": null,
  "volumes": [
    {
      "efsVolumeConfiguration": {
        "transitEncryptionPort": null,
        "fileSystemId": "<your EFS ID>",
        "authorizationConfig": {
          "iam": "DISABLED",
          "accessPointId": null
        },
        "transitEncryption": "DISABLED",
        "rootDirectory": "/"
      },
      "name": "<your EFS name>",
      "host": null,
      "dockerVolumeConfiguration": null
    }
  ]
}
```



## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the Creative Commons Attribution 4.0 License - see the LICENSE.md file for details

## References

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)