import json
from dotenv import load_dotenv
from fastapi import FastAPI
from enum import StrEnum
from collections import namedtuple

from fastapi.staticfiles import StaticFiles

from controllers import router

from app import app

# Load env file
load_dotenv()

app.include_router(router)
app.mount("/public", StaticFiles(directory="public"), name="public")
