Project contains two parts:
- backend/: FastAPI backend (Role 2)
- rule_engine/: Isolated rule engine (Role 3)

Run the rule engine tests:
1. cd rule_engine
2. pip install pyyaml
3. python test_cases.py

Run the backend:
1. cd backend
2. python run_migration.py
3. uvicorn main:app --reload
