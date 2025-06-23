# sqs2025

## Description
This is a project for learning purposes. It will consist of a webserver that contains the following features:
- Webserver
- Rest-Api
- Database
- Usermanagment
- User inventory
- Search engine for Pokemon
- Packopening for Pokemon
- Little Game with Pokemon
- Leaderboard

## Developer: Emre Gülcino

## Installation
Use the docker-compose file inside the repository:

### login to github package registry:
CR_PAT = Classic Access Token (Ask repositry owner to publish Access Token)
```bash
$ echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
$ docker-compose up
```
this will pull all the neccessary images and run the application.

## Access
The webpage will be available on port 8000:
```http://127.0.0.1:8000```

## Documentation
For api specific documentation visit the following page while the application is running:
```http://127.0.0.1:8000/docs```

For more indepth documentation visit the readthedocs:
```https://sqs2025.readthedocs.io/en/latest/```