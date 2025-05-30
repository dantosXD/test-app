from fastapi import FastAPI
from app.routers import auth_router, bases_router, tables_router, fields_router, records_router, ws_router, views_router, permissions_router, files_router # Import files_router
from app.database import engine, Base
# from app.websocket_manager import manager

# Base.metadata.create_all(bind=engine) # This should be handled by Alembic migrations

app = FastAPI(title="Airtable Clone API")

app.include_router(auth_router.router)
app.include_router(bases_router.router)
app.include_router(tables_router.router, tags=["tables"])
app.include_router(fields_router.router, tags=["fields"])
app.include_router(records_router.router, tags=["records"])
app.include_router(ws_router.router)
app.include_router(views_router.router, tags=["views"])
app.include_router(permissions_router.router)
app.include_router(files_router.router) # Include files_router

@app.get("/")
async def root():
    return {"message": "Welcome to the Airtable Clone API"}
