import yaml
import os
from typing import Dict, Any

class RuleEngine:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'rules.yaml')
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def _evaluate_operator(self, field_value: Any, operator: str, rule: Dict) -> bool:
        if operator == 'gte':
            return field_value >= rule['value']
        elif operator == 'gt':
            return field_value > rule['value']
        elif operator == 'lte':
            return field_value <= rule['value']
        elif operator == 'lt':
            return field_value < rule['value']
        elif operator == 'eq':
            return field_value == rule['value']
        elif operator == 'between':
            return rule['min'] <= field_value <= rule['max']
        elif operator == 'in':
            return field_value in rule['values']
        # lte_multiplier handled in run_eligibility for access to full profile
        return False

    def run_gap_analysis(self, report: Dict) -> Dict:
        gaps_found = []
        total_gain = 0

        for rule in self.config['gap_rules']:
            field_val = report.get(rule['field'])
            if field_val is None:
                continue
            
            operator = rule['operator']
            passed = False
            
            if operator == 'gt':
                passed = field_val > rule['value']
            elif operator == 'lt':
                passed = field_val < rule['value']
            elif operator == 'eq':
                passed = field_val == rule['value']
            
            if passed:
                action = rule['action_template'].replace('{current_value}', str(field_val))
                gaps_found.append({
                    "id": rule['id'],
                    "impact": rule['impact'],
                    "estimated_score_gain": rule['estimated_score_gain'],
                    "action": action
                })
                total_gain += rule['estimated_score_gain']

        impact_order = {'high': 0, 'medium': 1, 'low': 2}
        gaps_found.sort(key=lambda x: (impact_order.get(x['impact'], 3), -x['estimated_score_gain']))

        return {
            "customer_id": report.get('customer_id'),
            "mode": "gap_analysis",
            "gaps_found": len(gaps_found),
            "total_potential_score_gain": total_gain,
            "gaps": gaps_found
        }

    def run_eligibility(self, profile: Dict) -> Dict:
        rules_result = []
        fail_reasons = []
        passed_all = True

        group = self.config['eligibility_rules'][0]
        
        for rule in group['rules']:
            field_val = profile.get(rule['field'])
            if field_val is None:
                passed = False
            else:
                op = rule['operator']
                if op == 'gte':
                    passed = field_val >= rule['value']
                elif op == 'lte':
                    passed = field_val <= rule['value']
                elif op == 'between':
                    passed = rule['min'] <= field_val <= rule['max']
                elif op == 'in':
                    passed = field_val in rule['values']
                elif op == 'eq':
                    passed = field_val == rule['value']
                elif op == 'lte_multiplier':
                    multiplier_field_val = profile.get(rule['multiplier_field'], 0)
                    passed = field_val <= (multiplier_field_val * rule['multiplier'])
                else:
                    passed = False

            result = {"rule": rule['id'], "passed": passed}
            if not passed:
                result["reason"] = rule['message']
                fail_reasons.append(rule['id'])
                passed_all = False
            rules_result.append(result)

        next_step = "Improve CIBIL score by at least 30 points. See gap analysis." if 'cibil_score' in fail_reasons else "Review your application details."
        
        return {
            "customer_id": profile.get('customer_id'),
            "mode": "eligibility",
            "eligible": passed_all,
            "rules": rules_result,
            "fail_reasons": fail_reasons,
            "next_step": next_step
        }
