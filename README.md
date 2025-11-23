# Estrato Auth

Authentication service for the Estrato application, built with Python, FastAPI, and PostgreSQL.

## Tech Stack

* **Language:** Python 3.12
* **Framework:** FastAPI
* **Database:** PostgreSQL 16
* **ORM:** SQLAlchemy + Alembic
* **Testing:** Pytest
* **Security:** Python-Jose (JWT) + Passlib (Bcrypt)

## Configuration

1.  Clone the repository.
2.  Create a `.env` file based on the example:
    ```bash
    cp .env.example .env
    ```
3.  Populate the `.env` file with your variables (Database credentials, Secret Key, etc.).

## Running the Application (Docker)

To build and start the application (API + Database):

```bash
docker compose up --build -d
```

- The API will be available at: `http://localhost:8001`
- Migrations are applied automatically on startup.

## Documentation

Once running, access the interactive API documentation:

- **Swagger UI:** `http://localhost:8001/docs`

## Code Quality
To run the linter inside the container:

```bash
docker compose run --rm tests pylint src
```

## Running Tests

To run the integration and unit tests using the dedicated test container:

```bash
docker compose run --rm tests
```

## Stopping
To stop all containers:

```bash
docker compose down
```
