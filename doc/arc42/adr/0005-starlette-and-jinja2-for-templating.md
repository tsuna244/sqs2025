# 5. starlette and jinja2 for templating

Date: 2025-04-09

## Status

Accepted

## Context

This project needs a frontend the user can interact with. Since we use an api the easiest way is Web-Front-End

## Decision

For the frontend we use the templating of starlette and jinja2

## Consequences

### Pro
Its easy to implement since fastapi has already compability libraries included. It allows creating general templates that can be enhanced for later purposes.

### Con
The frontend still has to be programmed in HTML and javascript. This requires additional skills and time.

### Alternatives
For python there are no real templating alternatives. Even flask and Django use jinja2