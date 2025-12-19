#!/usr/bin/env python3
"""
Generate guidance and follow-up actions based on canonical JSON data.
Uses the colorectal ontology structure.
"""

import json
from rdflib import Graph, Namespace, Literal, RDF, URIRef
from mapper import EX, new_individual, add_data_property


def generate_guidance_from_canonical(canonical, graph):
    """
    Generate guidance and follow-up actions based on canonical JSON.
    Adds guidance individuals to the RDF graph.
    """
    
    # Find patient individual (assume it exists in graph)
    patient_id = None
    for subj, pred, obj in graph:
        if pred == RDF.type and obj == EX.Patient:
            patient_id = subj
            break
    
    if not patient_id:
        print("Warning: Patient not found in graph")
        return
    
    # Extract key data
    observations = canonical.get("observations", [])
    conditions = [c for c in canonical.get("conditions", []) if c.get("present", "").lower() == "true"]
    
    # Create observation lookup
    obs_map = {}
    for obs in observations:
        obs_map[obs.get("code", "")] = obs
    
    # Create condition lookup
    cond_codes = [c.get("code", "") for c in conditions]
    
    # Rule 1: High FIT + Symptoms → Urgent Referral
    fit_obs = obs_map.get("fit")
    if fit_obs:
        fit_value = float(fit_obs.get("value", 0) or 0)
        if fit_value > 100:
            has_symptoms = any(code in cond_codes for code in [
                "changeInBowelHabit", "rectalBleeding", "unintentionalWeightLoss"
            ])
            if has_symptoms:
                guidance_id = new_individual("guidance")
                graph.add((guidance_id, RDF.type, EX.Guidance))
                add_data_property(graph, guidance_id, "hasGuidanceCode", "URGENT_REFERRAL")
                add_data_property(graph, guidance_id, "hasGuidanceText", 
                    f"Urgent two-week-wait referral recommended. FIT result {fit_value} µg Hb/g is elevated, "
                    "combined with presenting symptoms (change in bowel habit, rectal bleeding, or weight loss).")
                add_data_property(graph, guidance_id, "hasPriorityLevel", "urgent")
                
                # Create follow-up action (ServiceRequest)
                action_id = new_individual("action")
                graph.add((action_id, RDF.type, EX.ServiceRequest))
                graph.add((action_id, RDF.type, EX.UrgentReferral))
                add_data_property(graph, action_id, "hasActionType", "urgent_referral")
                add_data_property(graph, action_id, "hasActionDescription", 
                    "Urgent two-week-wait colorectal referral required")
                add_data_property(graph, action_id, "hasTimeframe", "2 weeks")
                add_data_property(graph, action_id, "hasUrgency", "urgent")
                
                graph.add((guidance_id, EX.recommends, action_id))
                graph.add((patient_id, EX.hasFollowUpAction, action_id))
    
    # Rule 2: Iron Deficiency Anaemia + Family History → Consider Lynch Syndrome
    has_ida = "ironDeficiencyAnaemia" in cond_codes
    has_fh_crc = "familyHistoryOfColorectalCancer" in cond_codes
    
    if has_ida and has_fh_crc:
        guidance_id = new_individual("guidance")
        graph.add((guidance_id, RDF.type, EX.Guidance))
        add_data_property(graph, guidance_id, "hasGuidanceCode", "LYNCH_SCREENING")
        add_data_property(graph, guidance_id, "hasGuidanceText", 
            "Consider genetic testing for Lynch syndrome. Patient has iron deficiency anaemia "
            "and family history of colorectal cancer.")
        add_data_property(graph, guidance_id, "hasPriorityLevel", "moderate")
        
        action_id = new_individual("action")
        graph.add((action_id, RDF.type, EX.ServiceRequest))
        graph.add((action_id, RDF.type, EX.TreatmentRecommendation))
        add_data_property(graph, action_id, "hasActionType", "genetic_testing")
        add_data_property(graph, action_id, "hasActionDescription", 
            "Consider genetic testing for Lynch syndrome")
        add_data_property(graph, action_id, "hasTimeframe", "within 1 month")
        add_data_property(graph, action_id, "hasUrgency", "moderate")
        
        graph.add((guidance_id, EX.recommends, action_id))
        graph.add((patient_id, EX.hasFollowUpAction, action_id))
    
    # Rule 3: Low Haemoglobin + Low Ferritin → Iron Treatment
    hb_obs = obs_map.get("hb")
    ferritin_obs = obs_map.get("ferritin")
    
    if hb_obs and ferritin_obs:
        hb_value = float(hb_obs.get("value", 0) or 0)
        ferritin_value = float(ferritin_obs.get("value", 0) or 0)
        
        if hb_value < 120 and ferritin_value < 30:
            guidance_id = new_individual("guidance")
            graph.add((guidance_id, RDF.type, EX.Guidance))
            add_data_property(graph, guidance_id, "hasGuidanceCode", "IRON_TREATMENT")
            add_data_property(graph, guidance_id, "hasGuidanceText", 
                f"Consider iron supplementation. Haemoglobin {hb_value} g/L and Ferritin {ferritin_value} µg/L "
                "are below normal ranges.")
            add_data_property(graph, guidance_id, "hasPriorityLevel", "moderate")
            
            action_id = new_individual("action")
            graph.add((action_id, RDF.type, EX.MedicationRequest))
            graph.add((action_id, RDF.type, EX.TreatmentRecommendation))
            add_data_property(graph, action_id, "hasActionType", "iron_supplementation")
            add_data_property(graph, action_id, "hasActionDescription", 
                "Consider iron supplementation for iron deficiency anaemia")
            add_data_property(graph, action_id, "hasTimeframe", "immediate")
            add_data_property(graph, action_id, "hasUrgency", "moderate")
            
            graph.add((guidance_id, EX.recommends, action_id))
            graph.add((patient_id, EX.hasFollowUpAction, action_id))
    
    # Rule 4: Positive FIT + Age consideration → Colonoscopy
    if fit_obs:
        fit_value = float(fit_obs.get("value", 0) or 0)
        # Note: Age would need to be calculated from DOB if available
        if fit_value > 10:
            guidance_id = new_individual("guidance")
            graph.add((guidance_id, RDF.type, EX.Guidance))
            add_data_property(graph, guidance_id, "hasGuidanceCode", "COLONOSCOPY_RECOMMENDED")
            add_data_property(graph, guidance_id, "hasGuidanceText", 
                f"Colonoscopy investigation recommended. FIT result {fit_value} µg Hb/g is positive.")
            add_data_property(graph, guidance_id, "hasPriorityLevel", "high")
            
            action_id = new_individual("action")
            graph.add((action_id, RDF.type, EX.ServiceRequest))
            graph.add((action_id, RDF.type, EX.TreatmentRecommendation))
            add_data_property(graph, action_id, "hasActionType", "colonoscopy")
            add_data_property(graph, action_id, "hasActionDescription", 
                "Colonoscopy investigation required")
            add_data_property(graph, action_id, "hasTimeframe", "2 weeks")
            add_data_property(graph, action_id, "hasUrgency", "urgent")
            
            graph.add((guidance_id, EX.recommends, action_id))
            graph.add((patient_id, EX.hasFollowUpAction, action_id))
    
    # Rule 5: Multiple risk factors → Enhanced monitoring
    risk_factors = sum([
        fit_value > 100 if fit_obs and float(fit_obs.get("value", 0) or 0) > 100 else False,
        "changeInBowelHabit" in cond_codes,
        "rectalBleeding" in cond_codes,
        "unintentionalWeightLoss" in cond_codes,
        "ironDeficiencyAnaemia" in cond_codes,
        "familyHistoryOfColorectalCancer" in cond_codes
    ])
    
    if risk_factors >= 3:
        guidance_id = new_individual("guidance")
        graph.add((guidance_id, RDF.type, EX.Guidance))
        add_data_property(graph, guidance_id, "hasGuidanceCode", "ENHANCED_MONITORING")
        add_data_property(graph, guidance_id, "hasGuidanceText", 
            f"Enhanced monitoring recommended. Patient has {risk_factors} risk factors for colorectal cancer.")
        add_data_property(graph, guidance_id, "hasPriorityLevel", "high")
        
        # Create safety netting / enhanced monitoring (as ServiceRequest or CarePlan)
        action_id = new_individual("action")
        graph.add((action_id, RDF.type, EX.ServiceRequest))
        graph.add((action_id, RDF.type, EX.TreatmentRecommendation))
        # Could also be CarePlan for comprehensive safety netting
        add_data_property(graph, action_id, "hasActionType", "safety_netting")
        add_data_property(graph, action_id, "hasActionDescription", 
            f"Enhanced monitoring and safety netting required. Patient has {risk_factors} risk factors. "
            "Advise patient to return if symptoms worsen or new symptoms develop.")
        add_data_property(graph, action_id, "hasTimeframe", "ongoing")
        add_data_property(graph, action_id, "hasUrgency", "moderate")
        
        graph.add((guidance_id, EX.recommends, action_id))
        graph.add((patient_id, EX.hasFollowUpAction, action_id))


if __name__ == "__main__":
    # Load canonical JSON
    with open('canonical.json', 'r') as f:
        canonical = json.load(f)
    
    # Load existing ontology graph (from mapper.py output)
    from mapper import convert_canonical_to_ontology
    
    g = convert_canonical_to_ontology(canonical)
    
    # Generate guidance
    generate_guidance_from_canonical(canonical, g)
    
    # Output
    print(g.serialize(format="turtle"))

