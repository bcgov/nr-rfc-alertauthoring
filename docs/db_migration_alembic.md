# Database Migrations

## Environment variable Dependencies

To run this code there needs to be a database running, and the following env vars
in order for alembic to able to connect to the database.

* POSTGRES_USER
* POSTGRES_PASSWORD
* POSTGRES_HOST
* POSTGRES_DATABASE
* POSTGRES_PORT
* POSTGRES_SCHEMA

## install dependencies / activate env

make sure the dev dependencies have been installed,

``` sh
cd backend
poetry install

# activate the env
source $(poetry env info --path)/bin/activate
```

## Autogenerate a migration file

This step will look at the current state of the database vs the database
model definitions as defined in the v1.models package.  If differences
exist it will attempt to generate a new migration file.

Usually seems to be pretty good at picking database structural changes, 
however reviewing the output is always a good idea.

This step does not run the actual migration, but rather generates the
migration file.  Migration files will be located in the folder: `backend/alembic/versions`

``` sh
# load dev env vars from home directory or wherever the .env file is located
# alternatively load the env vars
set -o allexport; source .env; set +o allexport


alembic revision --autogenerate -m "migration message"
```

## Run the migration

Run all migrations
```
alembic upgrade head
```

Run up to a specific version
```
alembic upgrade <version>
```

## Revert / Rollback migration

```
alembic downgrade <version to revert to>

# revert back 1
alembic downgrade -1
```

## Create a blank empty migration

```
alembic revision -m "migration message"
```

# Docker Stuff

The 

## Build

`docker build -t alembic_migrations -f migrations/Dockerfile .`

## Run the container

`docker run -it --entrypoint /bin/sh alembic_migrations`