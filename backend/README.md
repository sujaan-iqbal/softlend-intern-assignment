# Softlend Backend API (Role 2)

## Setup Instructions
1. Navigate to the `backend/` folder.
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the migration: `python run_migration.py`
6. Start the server: `uvicorn main:app --reload`

## How to use
The API will be available at `http://127.0.0.1:8000`.
Interactive Swagger Docs available at `http://127.0.0.1:8000/docs`.

## Postman
Import `../postman_collection.json` into Postman to test all endpoints.
