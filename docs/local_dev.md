# Backend Developemtn

## Run backend


```sh
# init poetry env
source $(poetry env info --path)/bin/activate

# fire up backend
uvicorn src.main:app --host 0.0.0.0 --port 3003 --workers 1 --server-header --date-header --limit-concurrency 100 --reload --log-config ./logger.conf
```

## Database / Migrations

[db_migrations_docs](./db_migration_alembic.md)
