import sys
import os

# Get the absolute path to the project root folder
# We do this to import the rule_engine module from outside the backend folder
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from rule_engine.engine import RuleEngine

# Initialize the Rule Engine once
engine = RuleEngine()


# Bridge: Calls the Rule Engine Gap Analysis
def analyze_gaps(report_data):
    return engine.run_gap_analysis(report_data)


# Bridge: Calls the Rule Engine Eligibility Check
def check_eligibility(profile_data):
    return engine.run_eligibility(profile_data)
