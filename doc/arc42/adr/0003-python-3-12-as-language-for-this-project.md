# 3. Python 3.12 as language for this project

Date: 2025-04-09

## Status

Accepted

## Context

We have to deside on an environment for this project that helps including all the features while beeing compatible with our decision about the PokeAPI.

## Decision

This project will be written in python 3.12.

## Consequences

### Pro
Since we decided on pokebase we are forced to use python. But we can still decide the version. We will use 3.12 since the pokebase library supports python 3 versions up to 3.12. This will make sure we can use most of the newest updates for other libraries.

### Con
There may be libraries we wont be able to include in the future. This may leed to upgrading the version to 3.13. Of course only if pokebase supports that version in time.

### Alternatives
- **3.11**: This version has compability for the most libraries right now. But since this project does not require much of those libraries its better to keep a newer version for now. This ensures compability for newer libraries with additional features that may be needed in the future.