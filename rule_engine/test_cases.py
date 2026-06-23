import json
from engine import RuleEngine

engine = RuleEngine()

def run_test(name, mode, input_data):
    print(f"\n--- TEST: {name} ---")
    try:
        if mode == 'gap_analysis':
            result = engine.run_gap_analysis(input_data)
        else:
            result = engine.run_eligibility(input_data)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # 1. All gap rules fire
    run_test("1. All gap rules fire", "gap_analysis", {
        "customer_id": "C001",
        "credit_utilisation_pct": 87,
        "missed_payments_12m": 2,
        "written_off_accounts": 1,
        "credit_age_months": 14,
        "hard_enquiries_6m": 4
    })

    # 2. No gaps found
    run_test("2. No gaps found", "gap_analysis", {
        "customer_id": "C002",
        "credit_utilisation_pct": 20,
        "missed_payments_12m": 0,
        "written_off_accounts": 0,
        "credit_age_months": 48,
        "hard_enquiries_6m": 1
    })

    # 3. Action template substitution (covered by test 1)

    # 4. All eligibility rules pass
    run_test("4. All eligibility rules pass", "eligibility", {
        "customer_id": "C003",
        "age": 29,
        "cibil_score": 750,
        "monthly_income": 60000,
        "foir": 0.25,
        "employment_type": "salaried",
        "written_off_accounts": 0,
        "requested_amount": 400000
    })

    # 5. Multiple rules fail
    run_test("5. Multiple rules fail", "eligibility", {
        "customer_id": "C004",
        "age": 19,
        "cibil_score": 600,
        "monthly_income": 30000,
        "foir": 0.6,
        "employment_type": "unemployed",
        "written_off_accounts": 2,
        "requested_amount": 500000
    })

    # 6. Missing field in input
    print(f"\n--- TEST: 6. Missing field in input ---")
    try:
        result = engine.run_gap_analysis({
            "customer_id": "C005"
            # Deliberately missing all fields
        })
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Gracefully handled: {e}")
