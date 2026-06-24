# Softlend Rule Engine (Role 3)

The Rule Engine evaluates customer credit reports and generates credit-gap recommendations using configurable rules defined in `rules.yaml`.

## Setup

Install the required dependency:

```bash
pip install pyyaml
```

## Run Tests

Navigate to the Rule Engine directory and execute:

```bash
cd rule_engine
python test_cases.py
```

Sample outputs can be found in:

```text
test_output.txt
```

## Adding New Rules

All rules are maintained in:

```text
rules.yaml
```

To add a new rule:

1. Open `rules.yaml`
2. Add a rule under `gap_rules` or `eligibility_rules`
3. Save the file and rerun the tests

No changes to `engine.py` are required.

## Features

* YAML-based rule configuration
* Credit-gap analysis
* Eligibility evaluation
* Easily extensible without code changes
