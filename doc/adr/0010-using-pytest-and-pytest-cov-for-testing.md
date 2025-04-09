# 10. using pytest and pytest-cov for testing

Date: 2025-04-09

## Status

Accepted

## Context

The code has to be testet through the ci/cd pipeline

## Decision

We will use pytest and pytest-cov to create junit-results and coverage-results.

## Consequences

### Pro
Build in python tools. These are easy to implement inside the pipeline. We can also create artifacts that can be used by sonarcloud for example. Fastapi supports pytest.

### Con
Requires a setup. The project team has to learn how the pytest module functions and how the coverage is generated.

### Alternatives
- **github workflow orgoro**: the github workflow orgoro/coverage will allow to generate a coverage file without having to program it manually. But this allows for litte configuration.
- **tox**: this is a library that does the same as pytest-cov. It just uses a custom configuration. This is similar to pytest-cov and therefore the buildin version was used.
- **PyUnit**: This is more similar to java testing. But since fastapi already support pytest the team decided to stick with it.