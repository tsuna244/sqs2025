# 4. fastapi as REST-Api

Date: 2025-04-09

## Status

Accepted

## Context

This project will need a REST-Api as a feature.

## Decision

We will use the fastapi to implement the REST-Api

## Consequences

### Pro
The Projectteam has already a lot of knowledge and experience with the fastapi. Furthermore it allows even complex structures and features as well as integrated compability for modules like starlette or jinja2. This allows easy templating and including the frontend. It also comes with its own documentation generation.

### Con
It still a micro-web framework. It does not include a database.

### Alternatives
- **flask**: It has less functionality than fastapi. It may be enought for this project but for the future it would be better to use fastapi.
- **django**: This is a Full-Stack-Web framework which would be too much for this project. The functinality of Fastapi is sufficent for long time. This option would be considerable if the project will be rebuild with a much wider range of functions.

For a full comparision read the following article: https://www.geeksforgeeks.org/comparison-of-fastapi-with-django-and-flask/