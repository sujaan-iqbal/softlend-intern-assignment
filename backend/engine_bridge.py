import sys
import os

# Dynamically get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) # Goes up one level from 'backend' to root
sys.path.append(project_root)

from rule_engine.engine import RuleEngine

engine = RuleEngine()

def analyze_gaps(report_data):
    return engine.run_gap_analysis(report_data)

def check_eligibility(profile_data):
    return engine.run_eligibility(profile_data)