# Python FastAPI Backend
### Features
- [x] FastAPI
- [x] SQLAlchemy
- [x] SQLModel
- [x] Poetry
- [x] Prospector
- [x] Alembic
- [x] Docker
- [x] Docker Compose
- [x] GitHub Actions

## Getting Started

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Local Development

[Alembic Docs](../docs/db_migration_alembic.md)

#### Local Dev with Docker

* Wasn't able to get the frontend working in the docker compose so startup is 
  now a two step process

##### Backend Start

- Run the `docker compose up backend-py` command to start the backend stack.
- The database changes are applied automatically by alembic
- The source of the migrations are the SQLModels `backend/src/V1/models/model.py`
- Alembic versioned migration files are at `backend/alembic/versions`
- The API is Documentation available at http://localhost:3003/docs

##### Frontend Start

 - Navigate to the frontend directory `cd frontend/hydro_alerting`
 - Start the server with   `npm run start-local`
 - Establishes the proxy to the backend on the cli, vs deployed where it is handled by caddy
 - App URL is `http://localhost:4200`

#### Local Backend Dev - poetry

* create the env `cd backend; poetry install`
* activate the env `source $(poetry env info --path)/bin/activate`
* start uvicorn 

```uvicorn src.main:app --host 0.0.0.0 --port 3000 --workers 1 --server-header --date-header --limit-concurrency 100 --reload --log-config ./logger.conf```

### Unit Testing
- Run `docker-compose up -d backend-py-test` command to run the unit tests from the root directory.
- The folder is volume mounted , so any changes to the code will be reflected in the container and run the unit tests again.

