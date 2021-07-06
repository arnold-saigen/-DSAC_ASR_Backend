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
* AWS IAM roles

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

### Create your IAM policies and IAM role
You will need to create a AWS IAM policy and role for your service. This role is used to manage and access permisions for the microservices that are used.
See the following link to get started with IAM:
* [Getting started with IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started.html)
* You will need to create an IAM policy with similar permissions to the following:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "elasticfilesystem:*",
                "application-autoscaling:*",
                "s3:*",
                "cloudwatch:DeleteAlarms",
                "logs:*",
                "sns:CreateTopic",
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:ListMetrics",
                "sns:List*",
                "cloudwatch:PutMetricAlarm",
                "ecs:UpdateService",
                "cloudwatch:DescribeAlarmHistory",
                "iam:CreateServiceLinkedRole",
                "sns:Get*",
                "cloudwatch:EnableAlarmActions",
                "cloudwatch:DisableAlarmActions",
                "cloudwatch:DescribeAlarmsForMetric",
                "cloudwatch:DescribeAlarms",
                "ecs:*",
                "ecr:*",
                "ecs:DescribeServices",
                "sns:Subscribe"
            ],
            "Resource": "*"
        }
    ]
}
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

### Setting up an elastic file system (EFS) to host your models

You will need to create a Elastic File system which you will be using to store the ASR models. The file system is mounted to the containers at runtime.
See the following link to get started with EFS:
* [Getting started with EFS](https://docs.aws.amazon.com/efs/latest/ug/getting-started.html)

### Setting up ECS Fargate cluster and registering a task definition

* Create your own cluster with a unique name with the following command:
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
* Use JSON config file to create task definition
```
>> aws ecs register-task-definition --cli-input-json file://$HOME/tasks/fargate-task.json
```
* For more information follow the following link:
[Setting up a cluster and task definition](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_AWSCLI_Fargate.html)

### Creating a lambda function
You will need to create a Lambda function which will trigger each time an API request is made. This lambda functions serves to grab the required and optional parameters from the POST headers, verify the API key and check if all parameters are present. If all checks are passed, the Lambda function will start a Fargate task to do the decoding.
See the following link to get started with Lambda:
* [Getting started with Lambda](https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html)

### Creating an API Gateway and setting the Lambda trigger
You will need to create a API Gateway which serves as a Flask API and handels all HTTP traffic to the system.
See the following link to get started with API Gateway for Lambda:
* [Using AWS Lambda with Amazon API Gateway](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html)

## License

This project is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/legalcode) - see the LICENSE.md file for details

## References

Front-end) (https://github.com/fdmcgregor/SouthAfricanSpeechAnalyticsWebInterface)
