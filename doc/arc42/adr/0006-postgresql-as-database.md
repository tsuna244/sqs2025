# 6. postgresql as database

Date: 2025-04-09

## Status

Accepted

## Context

One of the features of the Project will be logging in and having an account. All the information must be safed in a database. Therefore we have to include one.

## Decision

This project will include postgresql as a database.

## Consequences

### Pro
Postgresql is a well known database that is sql based. There is already a library for python that allows easy access to the postresql DB. Furthermore there is a docker image that can be used to setup the DB very easy without installing it on the system itself. Additionally it has build in features like encrypt password saving that allow more secure ways of handling information. And its open source.

### Con
The python library may allow easy access but the sql code has still to be written by the developer himself. The functions for receiving and saving information therefore have to be programmed manualy.

### Alternatives
- **mysql**: Its a similar database like postgresql. But since the team has more experience with postgresql we decided against it.