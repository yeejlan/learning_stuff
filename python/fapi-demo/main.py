from fastapi.staticfiles import StaticFiles
from controllers import router
from bootstrap import app

app.include_router(router)
app.mount("/public", StaticFiles(directory="public"), name="public")

