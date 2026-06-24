# Softlend Credit Enablement System

This repository contains two independent modules:

* **backend/** – FastAPI backend implementing customer onboarding, credit profile management, offer lifecycle management, and EMI calculations.
* **rule_engine/** – Standalone credit gap analysis engine driven by configurable YAML rules.

---

## Repository Structure

```text
.
├── backend/
│   ├── migrations/
│   │   └── 001_init.sql
│   ├── .env
│   ├── README.md
│   ├── database.py
│   ├── engine_bridge.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── run_migration.py
│   └── schemas.py
│
├── rule_engine/
│   ├── README.md
│   ├── engine.py
│   ├── rules.yaml
│   ├── test_cases.py
│   └── test_output.txt
│
├── postman_collection.json
└── README.md
```

---

## Running the Rule Engine

Navigate to the rule engine directory:

```bash
cd rule_engine
```

Install dependencies:

```bash
pip install pyyaml
```

Execute the test suite:

```bash
python test_cases.py
```

This validates the rule engine against predefined credit-report scenarios and generates recommendations based on the configured rules.

---

## Running the Backend API

Navigate to the backend directory:

```bash
cd backend
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run database migrations:

```bash
python run_migration.py
```

Start the FastAPI application:

```bash
uvicorn main:app --reload
```

Backend will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```


---

## API Testing

Import the provided Postman collection:

```text
postman_collection.json
```

The collection includes:

* Customer creation and validation scenarios
* Credit score management
* Credit gap creation and resolution
* Credit profile retrieval
* Offer creation and filtering
* Offer status transitions
* EMI calculation
* Improvement summary endpoints
* Success and failure test cases for all major APIs

---

## Technology Stack

### Backend

* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* Python 3.x

### Rule Engine

* Python
* YAML-based rule configuration
* Rule evaluation engine

---

## Features

* Customer onboarding with PAN and mobile validation
* Credit score tracking
* Credit gap identification and resolution
* Potential credit score calculation
* Score-gated lending offers
* Offer lifecycle management
* EMI computation
* Improvement summary analytics
* Request logging middleware
* Migration-based database setup
* Environment-based configuration

