from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from backend.config import get_settings
from backend.api.routes import router


app = FastAPI(title="Meridian Electronics Support API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().get_cors_origins(),
    allow_origin_regex=get_settings().cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

lambda_handler = Mangum(app)
