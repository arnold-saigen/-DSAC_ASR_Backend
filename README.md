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

## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Contributors names and contact info

ex. Dominique Pizzie  
ex. [@DomPizzie](https://twitter.com/dompizzie)

## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)