# 8. dockerize the application

Date: 2025-04-09

## Status

Accepted

## Context

The project has to be deployed and make available for the end user. This should be as easy and bullet proof as possible.

## Decision

To achieve this, the application will run in a docker container. The system will be started via docker-compose. This will make sure everything works accordingly even on diffrent systems. The image for the Dockerfile will use the python:3.12-slim image.

## Consequences

### Pro
Dockerization will allow an easy setup and execution with a single docker-compose file. The install instructions will be easy to understand and fast to execute. Furthermore we can make sure that everything works in its set environment. This will allow to run the system on different OP systems without a lot of issues. Finaly we already mentiont the postgresql image as the database. Using a docker-compose file will make the setup much easier with custom configuration and easy access.

### Con
Intentionally the image python:3.12 should be used. But of today the image has 3 High vulnerablities. Therefore we will use the slim version of image. Additionaly using a docker container requires docker beeing setup on the system.

### Alternatives
- **python**: The only alternative would be instaling python on the system. This will allow running the application native but also requires setting up the postgresql database.