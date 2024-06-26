FROM python:3.12-alpine as build

# Disable cache dir, disable upgrade message, create .venv in project dir
ARG PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_IN_PROJECT=1

# Install poetry, then dependencies, include dev dependencies for migrations
# as alembic is a dev dependency
WORKDIR /app
RUN apk update && apk add --no-cache postgresql-dev gcc python3-dev musl-dev && \
    python3 -m venv venv && \
    . venv/bin/activate && \
    pip install sqlmodel alembic sqlalchemy psycopg2-binary pydantic pydantic[email] pydantic-settings


# # Run Migration
FROM python:3.12-alpine AS migrate
WORKDIR /app

COPY --from=build /app/venv /app/venv
COPY ./backend/src /app/src
COPY ./backend/alembic /app/alembic
COPY ./backend/alembic.ini /app/alembic.ini

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/venv/bin:$PATH"

# # Packages
RUN apk update && \
    apk add --no-cache libpq-dev 

USER 1001
HEALTHCHECK CMD [ "alembic", "show", "head" ]
ENTRYPOINT alembic upgrade head
