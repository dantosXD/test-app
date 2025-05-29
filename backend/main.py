from fastapi import FastAPI
from app.routers import auth_router, bases_router, tables_router, fields_router, records_router # Import records_router
from app.database import engine, Base # Import engine and Base
# from app import models # Import models if you need to create tables directly (not recommended with Alembic)

# Base.metadata.create_all(bind=engine) # This should be handled by Alembic migrations

app = FastAPI(title="Airtable Clone API")

app.include_router(auth_router.router)
app.include_router(bases_router.router)
app.include_router(tables_router.router, tags=["tables"])
app.include_router(fields_router.router, tags=["fields"])
app.include_router(records_router.router, tags=["records"]) # Include records_router

@app.get("/")
async def root():
    return {"message": "Welcome to the Airtable Clone API"}
