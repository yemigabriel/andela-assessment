from fastapi import FastAPI

from backend.api.routes import router


app = FastAPI(title="Meridian Electronics Support API", version="0.1.0")
app.include_router(router)
