from dotenv import load_dotenv

from fastapi.staticfiles import StaticFiles

from controllers import router

from app import app
from models import user_model


# Load env file
load_dotenv()

app.include_router(router)
app.mount("/public", StaticFiles(directory="public"), name="public")

