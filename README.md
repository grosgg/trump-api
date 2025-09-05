# Blackjack API
API managing users, blackjack games and their participations.

## Local development
Start the DB and web server with `docker compose up -d`.

## API documentation
Once the server is running, you can access the API documentation at [Swagger UI](http://localhost:8000/docs)

## Postman collection
A Postman collection is available at [trump-api.postman_collection.json](trump-api.postman_collection.json)

## Tech stack
- [FastAPI](https://fastapi.tiangolo.com/)
- [FastAPI-Users](https://fastapi-users.github.io/fastapi-users/)
- [PostgreSQL](https://www.postgresql.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [alembic](https://alembic.sqlalchemy.org/en/latest/)