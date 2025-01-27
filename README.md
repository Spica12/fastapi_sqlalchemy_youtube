# fastapi_sqlalchemy_youtube


## Lesson 2

```
poetry add fastapi

poetry add sqlalchemy[asyncio]

poetry add aiosqlite

poetry add pydantic-settings

poetry add uvicorn[standart]
```

## Lesson 3

```
poetry add alembic

alembic init -t async alembic

poetry add black --group dev

alembic revision --autogenerate -m "create_products_table"

alembic upgrade head
```
