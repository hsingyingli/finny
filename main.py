import os

from fastapi import FastAPI

app = FastAPI(title="Finny API")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://ai:ai@localhost:5532/ai")


@app.get("/")
async def root():
    return {"message": "Welcome to Finny API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
