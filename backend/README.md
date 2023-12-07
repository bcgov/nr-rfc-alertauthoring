# Python FastAPI Backend
### Features
- [x] FastAPI
- [x] SQLAlchemy
- [x] Poetry
- [x] Prospector
- [x] Flyway
- [x] Docker
- [x] Docker Compose
- [x] GitHub Actions

## Getting Started

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Local Development

#### Local Dev with Docker

- Run the `docker compose -f .\docker-compose.py.yml up` command to start the entire stack.
- The database changes are applied automatically by alembic
- The models are generated into `backend-py/src/v1/models/model.py` .
- The API is Documentation available at http://localhost:3003/docs

#### Local Dev - poetry

* create the env `cd backend; poetry install`
* activate the env `source $(poetry env info --path)/bin/activate`
* start uvicorn 

```uvicorn src.main:app --host 0.0.0.0 --port 3000 --workers 1 --server-header --date-header --limit-concurrency 100 --reload --log-config ./logger.conf```

### Unit Testing
- Run `docker-compose up -d backend-py-test` command to run the unit tests from the root directory.
- The folder is volume mounted , so any changes to the code will be reflected in the container and run the unit tests again.

