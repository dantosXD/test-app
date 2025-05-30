# Airtable Clone Backend

This directory contains the backend for the Airtable clone application, built with FastAPI.

## Setup and Running

### 1. Environment Variables

Create a `.env` file in this `backend` directory. This file will store your environment-specific configurations.
Copy the example below into your `.env` file and replace with your actual settings:

```env
DATABASE_URL="postgresql://user:password@localhost:5432/your_db_name"
SECRET_KEY="your_very_secret_key_for_jwt_32_chars_long_at_least"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Explanation:**

*   `DATABASE_URL`: The connection string for your PostgreSQL database.
    *   Example for local PostgreSQL: `postgresql://myuser:mypassword@localhost:5432/mydatabase`
    *   Ensure the database specified (e.g., `mydatabase`) exists before running migrations.
*   `SECRET_KEY`: A strong, random string used for signing JWTs. Keep this secure.
*   `ALGORITHM`: The algorithm used for JWT signing (HS256 is common).
*   `ACCESS_TOKEN_EXPIRE_MINUTES`: How long an access token remains valid.

### 2. Install Dependencies

It's highly recommended to use a Python virtual environment.

**Create a virtual environment (optional but recommended):**
Navigate to the `backend` directory first.
```bash
python3 -m venv venv
# or python -m venv venv
```

**Activate the virtual environment:**

*   On macOS and Linux:
    ```bash
    source venv/bin/activate
    ```
*   On Windows:
    ```bash
    .\venv\Scripts\activate
    ```

**Install dependencies:**

Once your virtual environment is activated (or if you choose to install globally), install the required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations

Alembic is used for database schema migrations. To apply all migrations and set up or update your database tables, ensure you are in the `backend` directory and run:

```bash
python -m alembic upgrade head
```

This command will apply all pending migrations found in `alembic/versions/`. New migration scripts (like `c08568358f6b_add_owner_id_to_tables_and_relationships.py` for adding table ownership) are added as the schema evolves. Running `upgrade head` ensures your database is up-to-date with the latest schema.

### 4. Run the FastAPI Application

To run the FastAPI development server, ensure you are in the `backend` directory:

```bash
uvicorn main:app --reload
```
The `main:app` refers to the `app` FastAPI instance in your `backend/main.py` file. The `--reload` flag enables auto-reloading on code changes.

The application will typically be available at `http://127.0.0.1:8000`. You can access the API documentation at `http://127.0.0.1:8000/docs`.

---

This setup provides a FastAPI backend with JWT authentication, database integration via SQLAlchemy, and schema management with Alembic. You can now proceed to interact with the API endpoints.
