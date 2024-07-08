from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from controllers import router
from bootstrap import app

# Load env file
load_dotenv()

app.include_router(router)
app.mount("/public", StaticFiles(directory="public"), name="public")

