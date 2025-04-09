# 2. Pokebase as API for this Project

Date: 2025-04-09

## Status

Accepted

## Context

In this project we have to use an opensource api. The aim of this Project is set to be a website including a search field and a little game including with pokemon. Therefore we will need an api and a wrapper that provides these informations. 

## Decision

We will use the pokebase wrapper for the PokeAPI. It is written in python

## Consequences

### Pro
This wrapper allows to access all the information that is provided by the PokeAPI with simple calls. It also comes with predefined functions that allow diffrent types of access. Be it with the id of a pokemon or its name. Furthermore it provides a function to access Sprites of a given pokemon. It also has auto caching as a feature.

### Con
Using this wrapper will force us to use Python as a programming language.

### Alternatives
- **pokepy**: Would be for python2/3 but this project will have a python version as requirement that will be python 3.x+. Therefore a python2 compability will not be needed.
- **pokeapi-reactor**: This wrapper would be for java (Spring Boot). The documentation was not clear enough to see all functions instanly, which lead to it not beeing used. Using this wrapper would take a lot of time until it can be used efficiently.
- **other**: In the documentation of the PokeAPI: https://pokeapi.co/docs/v2, there are a lot more alternatives that have diffrent features and requirements. But for this project we wanted to use ether Spring Boot or an Python Webserver. Therefore these options were not available for this project.
