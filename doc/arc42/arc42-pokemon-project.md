# arc42 Template – Pokémon Webserver Project

## 1. Introduction and Goals

### 1.1 Requirements Overview
This project is a Pokémon-themed web application where users can:
- Search for Pokémon by name.
- View a leaderboard of users and their points.
- Draw a random Pokémon from generation 1–3 and add it to his deck (only available to logged-in users).
- Customize their personal display of 6 Pokémon resulting in points (only available to logged-in users).

### 1.2 Quality Goals
- **Usability**: Simple and responsive UI for Pokémon interaction.
- **Security**: Authenticated routes for drawing and selection pages.
- **Maintainability**: Modular design with separate responsibilities.
- **Performance**: Fast responses for search and leaderboard views.

### 1.3 Stakeholders
| Stakeholder | Interest / Role                      |
|-------------|--------------------------------------|
| Developer   | Implements and maintains the system. |
| User        | Searches and customizes Pokémon.     |

---

## 2. Architecture Constraints

- Programming Language: Python
- Web Framework: FastAPI
- Authentication required for certain pages
- Pokémon data from external PokeAPI via pokebase wrapper
- PostgreSQL used for persistence via psycopg2 wrapper
- Project structured in self-contained modules under `/modules`

---

## 3. System Scope and Context

### 3.1 Business Context
The webserver enables Pokémon game-like interaction in a browser environment with personalized features and competitive scoring.

### 3.2 Technical Context

```
+-------------+      HTTP       +-----------------+
|   Browser   |  <----------->  |  Web Server API |
+-------------+                 +-----------------+
                                      |
                                      v
         +-----------------+   +------------------+
         | PokeAPI Module  |   | PostgreSQL Module|
         +-----------------+   +------------------+
                 |
                 v
         External PokeAPI Service
```

---

## 4. Solution Strategy

- Use a modular Python backend with modules for logging, Pokémon API access, and PostgreSQL interaction.
- Use HTML templates for dynamic pages and static files (CSS, JS).
- Authentication system protects pack-opening/display-selection routes.
- External integration with PokeAPI.
- PostgreSQL used for storing user data, decks, and points.

---

## 5. Building Block View
(TBD)
### 5.1 Whitebox Overall System
**Components**:
- `main.py`: Entry point of the webserver.
- `modules/logger-module.py`: Central logging utility.
- `modules/pokeapi-module.py`: Interface to PokeAPI.
- `modules/postgresql-module.py`: Database interface.
- `modules/interface/`: Common interface definitions.
- `static/`: CSS, JS.
- `templates/`: Jinja2 HTML templates.
- `init.py`: Module setup files.

### 5.2 Level 2: Modules
| Module                 | Responsibility                           |
|------------------------|-------------------------------------------|
| `logger-module.py`     | Standardized logging                      |
| `pokeapi-module.py`    | Fetching Pokémon data from PokeAPI        |
| `postgresql-module.py` | User and deck data persistence            |
| `main.py`              | Routing and controller logic              |

---

## 6. Runtime View

### 6.1 Search for Pokémon
1. User accesses homepage.
2. User submits search query.
3. Backend calls `pokeapi-module.py` to fetch and return data.
4. Data is rendered using templates.

### 6.2 Drawing Random Pokémon (Logged-in User)
1. User accesses pack opening page.
2. Backend verifies authentication.
3. User selects Generation 1-3
3. Random Pokémon from Gen 1–3 fetched via `pokeapi-module`.
4. Pokémon added to user’s deck via `postgresql-module`.

### 6.3 Selecting pokemon to display (Logged-in User)
1. User accesses display page.
2. Backend verifies authentication.
3. User select 6 Pokemon via dropdown menus.
4. Selected pokemon will be displayed via `pokeapi-module`
5. Frontend calculates Points and sends it to backand.
6. Adding points to user via `postgresql-module`

---

## 7. Deployment View

```
+------------------+        +------------------+
|  Client Browser  | <----> |  Python Web App  |
|                  |        |  (Flask/FastAPI) |
+------------------+        +------------------+
                                    |
                                    v
                +-------------------------+
                | PostgreSQL Database     |
                +-------------------------+
                + External PokeAPI        +
                +-------------------------+
```

---

## 8. Crosscutting Concepts

- **Authentication**: Required for deck modification and drawing Pokémon.
- **Logging**: Centralized via logger module.
- **Data Access Layer**: Encapsulated in PostgreSQL module.
- **Error Handling**: Graceful error logging and fallback messaging.
- **Routing**: Defined in `main.py`, uses templated views.

---

## 9. Design Decisions
(ADR)
- Use of modular design for maintainability.
- Chose PokeAPI as a lightweight, public Pokémon data provider.
- PostgreSQL for relational storage of user and deck data. Includes integrated security extention for password hashing.
- Static/declarative templates to simplify rendering logic.

---

## 10. Quality Scenarios

- **Usability**: Search is intuitive and results update quickly.
- **Security**: Only authenticated users can alter decks.
- **Availability**: If PokeAPI fails, show fallback message.
- **Performance**: PokeAPI calls are cached.

---

## 11. Risks and Technical Debt

- Dependency on third-party PokeAPI (no control over availability).
- Pokemon Games are very common, thus large competition.

---

## 12. Glossary

| Term        | Definition                                 |
|-------------|--------------------------------------------|
| PokeAPI     | Public API for Pokémon data                |
| Deck        | Set of Pokemon a user has in his inventory |
| Jinja       | Templating language for HTML in FastAPI    |