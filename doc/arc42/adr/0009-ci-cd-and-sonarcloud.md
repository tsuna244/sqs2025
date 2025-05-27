# 9. ci/cd and sonarcloud

Date: 2025-04-09

## Status

Accepted

## Context

Deploying the project and creating the docker image requires a lot of steps. Also the code has to be testet and checked to make sure it works the right way. To achieve this we will use a ci/cd pipeline that tests, scans and deploys the code. This will lead to a docker-image inside the package registry.

## Decision

In this project we will use github actions to implement the ci/cd pipeline. Scanning the code will be through sonarcloud.io.

## Consequences

### Pro
- **CI/CD**: this will allow automation for all the steps of the project. Github action is already integrated in our github repository.
- **sonarcloud**: this will make sure our code is safe and clean.

### Con
- **CI/CD**: Takes a lot of time to setup and is hard to check if it realy works or not.
- **sonarcloud**: We only use the free version. Therefore we can only check the main branch.

### Alternatives:
- **CI/CD**: There are no other options since github is a requirement.
- **Codacy**: The team never worked with this. The features are similar to sonarcloud. Therefore it was not choosen.
- **DeepSource**: While it is easer to setup and has most of sonarclouds functions it does not have SCA scans.