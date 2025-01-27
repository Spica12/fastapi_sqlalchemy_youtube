import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.config import settings
from app_v1 import router as router_v1

@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


app: FastAPI = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix=settings.api_v1_prefix)


@app.get("/")
def hello_index():
    return {
        "message": "Hello index!",
    }


@app.get("/hello/")
def hello(name: str = "World!"):
    name: str = name.strip().title()
    return {
        "message": f"Hello {name}!",
    }


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
