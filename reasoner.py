#!/usr/bin/env python3
"""
Reasoner for colorectal referral ontology.
Takes the ontology representation from mapper.py and performs reasoning
to generate clinical guidance and recommendations.
"""

from rdflib import Graph, Namespace, Literal, RDF, URIRef
from rdflib.plugins.sparql import prepareQuery
from mapper import EX, new_individual, add_data_property
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import json
import operator as op

class RuleEngine:
    """
    Engine for evaluating declarative rules defined in JSON format.
    """
    
    # Operator mapping
    OPERATORS = {
        ">": op.gt,
        ">=": op.ge,
        "<": op.lt,
        "<=": op.le,
        "==": op.eq,
        "!=": op.ne,
    }
    
    def __init__(self, rules_config: Dict[str, Any]):
        """
        Initialize the rule engine with rule definitions.
        
        Args:
            rules_config: Dictionary containing rule definitions (from JSON file)
        """
        self.rules = rules_config.get("rules", [])
    
    def evaluate_rule(self, rule: Dict[str, Any], patient_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluate a single rule against patient data.
        
        Args:
            rule: Rule definition dictionary
            patient_data: Extracted patient data
            
        Returns:
            Dictionary with guidance and actions if rule matches, None otherwise
        """
        conditions = rule.get("conditions", {})
        
        # Evaluate all condition groups (all must pass)
        if not self._evaluate_conditions(conditions, patient_data):
            return None
        
        # Rule matched - generate guidance and actions
        guidance = rule.get("guidance", {})
        actions = rule.get("actions", [])
        
        # Format guidance text template with patient data values
        guidance_text = self._format_template(
            guidance.get("text_template", ""),
            patient_data
        )
        
        # Format action descriptions
        formatted_actions = []
        for action in actions:
            formatted_action = action.copy()
            if "description" in formatted_action:
                formatted_action["description"] = self._format_template(
                    formatted_action["description"],
                    patient_data
                )
            formatted_actions.append(formatted_action)
        
        return {
            "guidance": {
                "code": guidance.get("code", ""),
                "text": guidance_text,
                "priority": guidance.get("priority", "moderate")
            },
            "actions": formatted_actions
        }
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """
        Evaluate condition groups. All top-level condition groups must pass.
        
        Args:
            conditions: Conditions dictionary
            patient_data: Patient data
            
        Returns:
            True if all conditions pass, False otherwise
        """
        # All top-level condition groups must pass (AND logic)
        for condition_type, condition_def in conditions.items():
            if not self._evaluate_condition_group(condition_type, condition_def, patient_data):
                return False
        return True
    
    def _evaluate_condition_group(self, condition_type: str, condition_def: Dict[str, Any], 
                                  patient_data: Dict[str, Any]) -> bool:
        """
        Evaluate a specific condition group.
        
        Args:
            condition_type: Type of condition (observations, conditions, family_history, risk_factors)
            condition_def: Condition definition
            patient_data: Patient data
            
        Returns:
            True if condition passes, False otherwise
        """
        if condition_type == "observations":
            return self._evaluate_observations(condition_def, patient_data)
        elif condition_type == "conditions":
            return self._evaluate_conditions_list(condition_def, patient_data)
        elif condition_type == "family_history":
            return self._evaluate_family_history(condition_def, patient_data)
        elif condition_type == "risk_factors":
            return self._evaluate_risk_factors(condition_def, patient_data)
        else:
            return False
    
    def _evaluate_observations(self, obs_conditions: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Evaluate observation conditions."""
        observations = patient_data.get("observations", {})
        
        # All observation conditions must pass (AND logic)
        for obs_code, obs_condition in obs_conditions.items():
            obs_data = observations.get(obs_code)
            if not obs_data or not obs_data.get("value"):
                return False
            
            value = obs_data["value"]
            operator_str = obs_condition.get("operator")
            threshold = obs_condition.get("threshold")
            
            if operator_str not in self.OPERATORS:
                return False
            
            if not self.OPERATORS[operator_str](value, threshold):
                return False
        
        return True
    
    def _evaluate_conditions_list(self, cond_conditions: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Evaluate condition list conditions (any_of, all_of)."""
        patient_conditions = patient_data.get("conditions", [])
        
        if "any_of" in cond_conditions:
            # At least one condition must be present
            required = cond_conditions["any_of"]
            return any(cond in patient_conditions for cond in required)
        
        elif "all_of" in cond_conditions:
            # All conditions must be present
            required = cond_conditions["all_of"]
            return all(cond in patient_conditions for cond in required)
        
        return False
    
    def _evaluate_family_history(self, fh_conditions: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Evaluate family history conditions."""
        family_history = patient_data.get("family_history", [])
        
        if "any_contains" in fh_conditions:
            # At least one family history entry must contain any of the search terms
            search_terms = fh_conditions["any_contains"]
            for fh_entry in family_history:
                condition_text = (fh_entry.get("condition") or "").lower()
                if any(term.lower() in condition_text for term in search_terms):
                    return True
            return False
        
        return False
    
    def _evaluate_risk_factors(self, risk_conditions: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Evaluate risk factor conditions."""
        min_count = risk_conditions.get("min_count", 0)
        factors = risk_conditions.get("factors", [])
        
        count = 0
        for factor in factors:
            factor_type = factor.get("type")
            factor_code = factor.get("code")
            
            if factor_type == "observation":
                obs_data = patient_data.get("observations", {}).get(factor_code)
                if obs_data and obs_data.get("value") is not None:
                    value = obs_data["value"]
                    operator_str = factor.get("operator")
                    threshold = factor.get("threshold")
                    
                    if operator_str and threshold:
                        if operator_str in self.OPERATORS:
                            if self.OPERATORS[operator_str](value, threshold):
                                count += 1
                    else:
                        # Just check if observation exists
                        count += 1
            
            elif factor_type == "condition":
                if factor_code in patient_data.get("conditions", []):
                    count += 1
        
        return count >= min_count
    
    def _format_template(self, template: str, patient_data: Dict[str, Any]) -> str:
        """Format template string with patient data values."""
        if not template:
            return ""
        
        # Extract observation values for template
        observations = patient_data.get("observations", {})
        fit_obs = observations.get("fit", {})
        hb_obs = observations.get("hb", {})
        ferritin_obs = observations.get("ferritin", {})
        
        # Calculate risk factor count
        risk_factors = []
        fit_value = fit_obs.get("value", 0) if fit_obs else 0
        if fit_value > 100:
            risk_factors.append("high_fit")
        if "changeInBowelHabit" in patient_data.get("conditions", []):
            risk_factors.append("change_bowel")
        if "rectalBleeding" in patient_data.get("conditions", []):
            risk_factors.append("rectal_bleeding")
        if "unintentionalWeightLoss" in patient_data.get("conditions", []):
            risk_factors.append("weight_loss")
        if "ironDeficiencyAnaemia" in patient_data.get("conditions", []):
            risk_factors.append("ida")
        if "familyHistoryOfColorectalCancer" in patient_data.get("conditions", []):
            risk_factors.append("fh_crc")
        
        # Template variables
        template_vars = {
            "fit_value": fit_obs.get("value", "N/A") if fit_obs else "N/A",
            "hb_value": hb_obs.get("value", "N/A") if hb_obs else "N/A",
            "ferritin_value": ferritin_obs.get("value", "N/A") if ferritin_obs else "N/A",
            "risk_factor_count": len(risk_factors),
        }
        
        try:
            return template.format(**template_vars)
        except KeyError:
            # If template variable not found, return template as-is
            return template
    
    def evaluate_all_rules(self, patient_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate all rules and return matching results.
        
        Args:
            patient_data: Extracted patient data
            
        Returns:
            List of rule results (guidance + actions) for matching rules
        """
        results = []
        for rule in self.rules:
            result = self.evaluate_rule(rule, patient_data)
            if result:
                results.append(result)
        return results


class ColorectalReasoner:
    """
    Reasoner that takes patient data (from mapper.py output) and generates
    clinical guidance and recommendations based on the ontology rules.
    
    Can accept either:
    - TTL file path (e.g., "onto.ttl") - the serialized output from mapper.py
    - RDF Graph object - the graph directly from mapper.py
    
    NOTE: Currently, the reasoning rules are defined in Python code (hardcoded).
    The ontology file (colorectal_ontology.ttl) contains rule descriptions as comments
    but not executable rule definitions. For a more declarative approach, see
    reasoning_rules.json which defines rules in a structured format.
    """
    
    def __init__(self, ontology_file: Optional[str]= "colorectal_ontology.ttl", rules_file: Optional[str] = "reasoning_rules.json"):
        """
        Initialize the reasoner with the base ontology.
        
        Args:
            ontology_file: Path to the colorectal ontology TTL file
            rules_file: Optional path to JSON file with rule definitions.
                       If None, uses hardcoded Python rules (current default).
        """
        self.ontology_file = ontology_file
        self.ontology = Graph()
        self.ontology.parse(ontology_file, format="turtle")
        self.ontology.bind("ex", EX)
        
        # Load rules from file if provided, otherwise use hardcoded rules
        self.rules_file = rules_file
        self.rules_config = None
        self.rule_engine = None
        if rules_file:
            with open(rules_file, 'r') as f:
                self.rules_config = json.load(f)
            # Initialize rule engine for declarative rules
            self.rule_engine = RuleEngine(self.rules_config)
        
    def reason(self, patient_data_input) -> Dict[str, Any]:
        """
        Perform reasoning on the patient data graph.
        
        Args:
            patient_data_input: Either:
                - Path to TTL file (string) containing patient data from mapper.py (e.g., "onto.ttl")
                - RDF Graph object from mapper.py containing patient data
                
        Returns:
            Dictionary containing:
            - guidance: List of guidance recommendations
            - actions: List of follow-up actions
            - risk_assessment: Risk factors and assessment
            - summary: Overall summary
        """
        # Use RDF graph + SPARQL approach (reliable and works with TTL files)
        # Load patient graph from file if string is provided, otherwise use the graph directly
        if isinstance(patient_data_input, str):
            # Input is a file path
            patient_graph = Graph()
            patient_graph.parse(patient_data_input, format="turtle")
            patient_graph.bind("ex", EX)
        else:
            # Input is already a Graph object
            patient_graph = patient_data_input
        
        # Merge patient graph with ontology
        combined_graph = Graph()
        combined_graph += self.ontology
        combined_graph += patient_graph
        combined_graph.bind("ex", EX)
        
        # Use RDF graph + SPARQL approach for reasoning
        return self._reason_with_rdflib(patient_data_input)
    
    def _reason_with_rdflib(self, patient_data_input) -> Dict[str, Any]:
        """
        Primary reasoning method using RDF graph and SPARQL queries.
        Extracts patient data from the graph and uses the rule engine to evaluate rules.
        """
        from rdflib import Graph, Namespace, RDF
        from rdflib.plugins.sparql import prepareQuery
        
        # Load ontology and patient data using rdflib
        ontology_graph = Graph()
        ontology_graph.parse(self.ontology_file, format="turtle")
        
        if isinstance(patient_data_input, str):
            patient_graph = Graph()
            patient_graph.parse(patient_data_input, format="turtle")
        else:
            patient_graph = patient_data_input
        
        # Merge graphs
        combined_graph = Graph()
        combined_graph += ontology_graph
        combined_graph += patient_graph
        combined_graph.bind("ex", EX)
        
        # Extract patient data from the graph
        patient_data = self._extract_patient_data(combined_graph)
        
        if not patient_data["patient_id"]:
            return {
                "guidance": [],
                "actions": [],
                "risk_assessment": {"risk_level": "UNKNOWN", "risk_score": 0, "risk_factors": [], "total_factors": 0},
                "summary": "No patient found in data"
            }
        
        # Use rule engine if available (declarative rules from JSON), otherwise use hardcoded rules
        guidance_list = []
        actions_list = []
        
        if self.rule_engine:
            # Evaluate declarative rules from JSON
            rule_results = self.rule_engine.evaluate_all_rules(patient_data)
            for result in rule_results:
                guidance_list.append(result["guidance"])
                actions_list.extend(result["actions"])
            print("used rule engine")
        else: 
            print("initialize rule engine");
        # else:
        #     # Fall back to hardcoded Python rules
        #     # Rule 1: High FIT + Symptoms → Urgent Referral
        #     rule1_result = self._rule_high_fit_symptoms(combined_graph, patient_data)
        #     if rule1_result:
        #         guidance_list.append(rule1_result["guidance"])
        #         actions_list.extend(rule1_result["actions"])
            
        #     # Rule 2: Iron Deficiency Anaemia + Family History → Lynch Syndrome
        #     rule2_result = self._rule_ida_family_history(combined_graph, patient_data)
        #     if rule2_result:
        #         guidance_list.append(rule2_result["guidance"])
        #         actions_list.extend(rule2_result["actions"])
            
        #     # Rule 3: Low Haemoglobin + Low Ferritin → Iron Treatment
        #     rule3_result = self._rule_low_hb_ferritin(combined_graph, patient_data)
        #     if rule3_result:
        #         guidance_list.append(rule3_result["guidance"])
        #         actions_list.extend(rule3_result["actions"])
            
        #     # Rule 4: Positive FIT → Colonoscopy
        #     rule4_result = self._rule_positive_fit_colonoscopy(combined_graph, patient_data)
        #     if rule4_result:
        #         guidance_list.append(rule4_result["guidance"])
        #         actions_list.extend(rule4_result["actions"])
            
        #     # Rule 5: Multiple risk factors → Enhanced monitoring
        #     rule5_result = self._rule_multiple_risk_factors(combined_graph, patient_data)
        #     if rule5_result:
        #         guidance_list.append(rule5_result["guidance"])
        #         actions_list.extend(rule5_result["actions"])
        
        # Calculate risk assessment
        risk_assessment = self._calculate_risk_assessment(patient_data)
        
        # Generate summary
        summary = self._generate_summary(patient_data, guidance_list, risk_assessment)
        
        return {
            "guidance": guidance_list,
            "actions": actions_list,
            "risk_assessment": risk_assessment,
            "summary": summary,
            "patient_data": patient_data
        }
    
    def _extract_patient_data(self, graph: Graph) -> Dict[str, Any]:
        """Extract structured patient data from the graph."""
        patient_data = {
            "patient_id": None,
            "observations": {},
            "conditions": [],
            "age": None,
            "family_history": []
        }
        
        # Find patient
        query = prepareQuery(
            """
            SELECT ?patient ?dob ?sex
            WHERE {
                ?patient a ex:Patient .
                OPTIONAL { ?patient ex:hasDOB ?dob . }
                OPTIONAL { ?patient ex:hasSex ?sex . }
            }
            """,
            initNs={"ex": EX}
        )
        
        for row in graph.query(query):
            patient_data["patient_id"] = row.patient
            if row.dob:
                dob_str = str(row.dob)
                try:
                    dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                    patient_data["age"] = (date.today() - dob).days // 365
                except:
                    pass
            if row.sex:
                patient_data["sex"] = str(row.sex)
        
        if not patient_data["patient_id"]:
            return patient_data
        
        # Extract observations
        obs_query = prepareQuery(
            """
            SELECT ?obs ?code ?value ?unit ?type
            WHERE {
                ?obs a ?type .
                ?obs ex:observedFor ?patient .
                OPTIONAL { ?obs ex:hasCode ?code . }
                OPTIONAL { ?obs ex:hasNumericValue ?value . }
                OPTIONAL { ?obs ex:hasUnit ?unit . }
            }
            """,
            initNs={"ex": EX}
        )
        
        for row in graph.query(obs_query, initBindings={"patient": patient_data["patient_id"]}):
            obs_type = str(row.type).split("#")[-1] if row.type else None
            code = str(row.code) if row.code else None
            value = float(row.value) if row.value else None
            unit = str(row.unit) if row.unit else None
            
            # Map observation type to code
            if obs_type == "FIT_Result":
                code = "fit"
            elif obs_type == "Haemoglobin_Result":
                code = "hb"
            elif obs_type == "Ferritin_Result":
                code = "ferritin"
            elif obs_type == "MCV_Result":
                code = "mcv"
            elif obs_type == "Creatinine_Result":
                code = "creatinine"
            elif obs_type == "eGFR_Result":
                code = "egfr"
            elif obs_type == "Coeliac_TTG_Result":
                code = "ttg"
            elif obs_type == "UrineDipstick_Result":
                code = "urineDipstick"
            
            if code:
                patient_data["observations"][code] = {
                    "value": value,
                    "unit": unit,
                    "type": obs_type
                }
        
        # Extract conditions
        cond_query = prepareQuery(
            """
            SELECT ?cond ?code ?type
            WHERE {
                ?cond a ?type .
                ?cond ex:affects ?patient .
                OPTIONAL { ?cond ex:hasCode ?code . }
            }
            """,
            initNs={"ex": EX}
        )
        
        for row in graph.query(cond_query, initBindings={"patient": patient_data["patient_id"]}):
            cond_type = str(row.type).split("#")[-1] if row.type else None
            code = str(row.code) if row.code else None
            
            # Map condition type to code
            if cond_type:
                code_map = {
                    "ChangeInBowelHabit": "changeInBowelHabit",
                    "RectalBleeding": "rectalBleeding",
                    "AnalMass": "analMass",
                    "RectalMass": "rectalMass",
                    "IronDeficiencyAnaemia": "ironDeficiencyAnaemia",
                    "UnintentionalWeightLoss": "unintentionalWeightLoss",
                    "AbdominalMass": "abdominalMass",
                    "FamilyHistoryOfColorectalCancer": "familyHistoryOfColorectalCancer"
                }
                if cond_type in code_map:
                    code = code_map[cond_type]
            
            if code:
                patient_data["conditions"].append(code)
        
        # Extract family history
        fh_query = prepareQuery(
            """
            SELECT ?fh ?relative ?condition
            WHERE {
                ?fh a ex:FamilyMemberHistory .
                ?fh ex:familyHistoryFor ?patient .
                OPTIONAL { ?fh ex:hasRelative ?relative . }
                OPTIONAL { ?fh ex:hasCondition ?condition . }
            }
            """,
            initNs={"ex": EX}
        )
        
        for row in graph.query(fh_query, initBindings={"patient": patient_data["patient_id"]}):
            patient_data["family_history"].append({
                "relative": str(row.relative) if row.relative else None,
                "condition": str(row.condition) if row.condition else None
            })
        
        return patient_data
 
    def _calculate_risk_assessment(self, patient_data: Dict) -> Dict[str, Any]:
        """Calculate overall risk assessment."""
        risk_factors = []
        risk_score = 0
        
        # FIT > 100
        fit_obs = patient_data["observations"].get("fit")
        if fit_obs and fit_obs.get("value", 0) > 100:
            risk_factors.append("High FIT result (>100 µg Hb/g)")
            risk_score += 3
        
        # Symptoms
        if "changeInBowelHabit" in patient_data["conditions"]:
            risk_factors.append("Change in bowel habit")
            risk_score += 1
        if "rectalBleeding" in patient_data["conditions"]:
            risk_factors.append("Rectal bleeding")
            risk_score += 2
        if "unintentionalWeightLoss" in patient_data["conditions"]:
            risk_factors.append("Unintentional weight loss")
            risk_score += 2
        
        # Anaemia
        if "ironDeficiencyAnaemia" in patient_data["conditions"]:
            risk_factors.append("Iron deficiency anaemia")
            risk_score += 2
        
        # Family history
        if "familyHistoryOfColorectalCancer" in patient_data["conditions"] or \
           any(fh.get("condition", "").lower().find("colorectal") >= 0 
               for fh in patient_data["family_history"]):
            risk_factors.append("Family history of colorectal cancer")
            risk_score += 1
        
        # Age
        age = patient_data.get("age")
        if age and age >= 50:
            risk_factors.append(f"Age ≥50 years (current age: {age})")
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 5:
            risk_level = "HIGH"
        elif risk_score >= 3:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "total_factors": len(risk_factors)
        }
    
    def _generate_summary(self, patient_data: Dict, guidance_list: List, risk_assessment: Dict) -> str:
        """Generate overall summary."""
        summary_parts = []
        
        summary_parts.append(f"Patient Risk Assessment: {risk_assessment['risk_level']} (Score: {risk_assessment['risk_score']})")
        summary_parts.append(f"Identified {risk_assessment['total_factors']} risk factors.")
        
        if guidance_list:
            summary_parts.append(f"\nGenerated {len(guidance_list)} guidance recommendations:")
            for i, guidance in enumerate(guidance_list, 1):
                summary_parts.append(f"  {i}. [{guidance['code']}] {guidance['text']}")
        
        return "\n".join(summary_parts)



if __name__ == "__main__":

    # Option 1: Use TTL file output from mapper.py with declarative rules
    reasoner = ColorectalReasoner()
    results = reasoner.reason("onto.ttl")
    
    # Output results
    print("=" * 80)
    print("REASONING RESULTS")
    print("=" * 80)
    print("\n" + results["summary"])
    print("\n" + "=" * 80)
    print("DETAILED GUIDANCE")
    print("=" * 80)
    for guidance in results["guidance"]:
        print(f"\n[{guidance['code']}] {guidance['priority'].upper()}")
        print(f"  {guidance['text']}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDED ACTIONS")
    print("=" * 80)
    for action in results["actions"]:
        print(f"\n{action['type'].upper()}: {action['description']}")
        print(f"  Timeframe: {action['timeframe']}")
        print(f"  Urgency: {action['urgency']}")
    
    print("\n" + "=" * 80)
    print("RISK ASSESSMENT")
    print("=" * 80)
    print(f"Risk Level: {results['risk_assessment']['risk_level']}")
    print(f"Risk Score: {results['risk_assessment']['risk_score']}")
    print(f"Risk Factors ({results['risk_assessment']['total_factors']}):")
    for factor in results['risk_assessment']['risk_factors']:
        print(f"  - {factor}")
    
    # Optionally save results as JSON
    with open('reasoning_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print("\nResults saved to reasoning_results.json")

