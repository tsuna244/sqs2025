# 7. logging integration

Date: 2025-04-09

## Status

Accepted

## Context

It is necessary to import a logging system. This will make sure we can see if issues accure and why they do.

## Decision

To implement the logging we will use the logger module of python. The implementation will be realised with a singelton logger class.

## Consequences

### Pro
This will make sure there is only one logger for the whole system. Additionally, we can create a logging with a filehandler as well as a streamhandler. These configurations can be extended later on.

### Con
Since we use a singelton logger, all systems will write to the same log file. This might be an issue if the project becomes very large.

### Alternatives
- **jsonlogger**: this logger allows structural logging. This may be useful if the project becomes large since even with a singelton module it could be realisable. But in this project the build in logging is enough.
- **loguru**: this is a third-party logging framework for python. It has similar features to the native logging module as well as jsonlogger. Yet again this would be more useful for a larger project. It could be easily implemented in the current system tho.