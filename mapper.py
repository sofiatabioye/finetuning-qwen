FHIR_TO_OWL_MAP = {
    "Patient": {
        "class": ":Patient",
        "id_prefix": "patient",
        "properties": {
            "id": ":hasId",
            "name": ":hasName",
            "sex": ":hasSex",
            "dob": ":hasDOB",
            "ethnicity": ":hasEthnicity",
            "language": ":hasLanguage",
            "hospitalNumber": ":hasHospitalNumber",
            "address": ":hasAddress",
            "nhsNumber": ":hasNHSNumber",
            "contact.mobile": ":hasMobile",
            "contact.landline": ":hasLandline",
            "contact.email": ":hasEmail",
            "smokingStatus": ":hasSmokingStatus",
            "alcoholUnitsPerWeek": ":hasAlcoholUnitsPerWeek",
            "alcoholPattern": ":hasAlcoholPattern"
        }
    },
    "Organization": {
        "class": ":Organization",
        "id_prefix": "org",
        "properties": {
            "id": ":hasId",
            "name": ":hasName",
            "odsCode": ":hasODSCode",
            "telephone": ":hasTelephone",
            "fax": ":hasFax",
            "email": ":hasEmail"
        }
    },
    "Encounter": {
        "class": ":Encounter",
        "id_prefix": "enc",
        "properties": {
            "id": ":hasId",
            "date": ":hasDate",
            "reason": ":hasReason",
            "location": ":hasLocation",
            "interpreterRequired": ":hasInterpreterRequired",
            "capacityToConsent": ":hasCapacityToConsent",
            "whoPerformanceStatus": ":hasWHOPerformanceStatus",
            "rawText": ":hasRawText",
            "cancer_type": ":hasCancerType"
        },
        "relations": {
            "subject": ":encounterFor"
        }
    },
    "Referral": {
        "class": ":Referral",
        "id_prefix": "ref",
        "properties": {
            "id": ":hasId",
            "service": ":hasService",
            "priority": ":hasPriority",
            "referrerName": ":hasReferrerName",
            "practiceName": ":hasPracticeName",
            "dateOfDecisionToRefer": ":hasDateOfDecisionToRefer",
            "dateOfReferral": ":hasDateOfReferral",
            "consentToText": ":hasConsentToText",
            "gpDeclaration": ":hasGPDeclaration"
        },
        "relations": {
            "subject": ":referralFor"
        }
    },
    "Observation": {
        "class_map": {   # Map observation codes to classes
            "fit": ":FIT_Result",
            "hb": ":Haemoglobin_Result",
            "ferritin": ":Ferritin_Result",
            "mcv": ":MCV_Result",
            "creatinine": ":Creatinine_Result",
            "egfr": ":eGFR_Result",
            "ttg": ":Coeliac_TTG_Result",
            "urineDipstick": ":UrineDipstick_Result",
        },
        "id_prefix": "obs",
        "properties": {
            "id": ":hasId",
            "code": ":hasCode",
            "display": ":hasDisplay",
            "value": ":hasNumericValue",
            "unit": ":hasUnit",
            "date": ":hasDate",
            "status": ":hasStatus"
        },
        "relations": {
            "subject": ":observedFor"
        }
    },
    "Condition": {
        "class_map": {
            "changeInBowelHabit": ":ChangeInBowelHabit",
            "rectalBleeding": ":RectalBleeding",
            "analMass": ":AnalMass",
            "rectalMass": ":RectalMass",
            "ironDeficiencyAnaemia": ":IronDeficiencyAnaemia",
            "unintentionalWeightLoss": ":UnintentionalWeightLoss",
            "abdominalMass": ":AbdominalMass",
            "familyHistoryOfColorectalCancer": ":FamilyHistoryOfColorectalCancer",
        },
        "id_prefix": "cond",
        "properties": {
            "id": ":hasId",
            "code": ":hasCode",
            "display": ":hasDisplay",
            "present": ":hasPresent",
            "status": ":hasStatus"
        },
        "relations": {
            "subject": ":affects"
        }
    },
    "Medication": {
        "class": ":Medication",
        "id_prefix": "med",
        "properties": {
            "id": ":hasId",
            "name": ":hasMedicationName",
            "doseText": ":hasDoseText",
            "status": ":hasStatus"
        },
        "relations": {
            "subject": ":forPatient"
        }
    },
    "Allergy": {
        "class": ":AllergyIntolerance",
        "id_prefix": "alg",
        "properties": {
            "id": ":hasId",
            "substance": ":hasSubstance",
            "reaction": ":hasReaction",
            "criticality": ":hasCriticality"
        },
        "relations": {
            "subject": ":allergyFor"
        }
    },
    # Note: History items map to appropriate FHIR resources:
    # - Medical history → Condition (with status: active/historical)
    # - Procedures → Procedure
    # - Family history → FamilyMemberHistory
    # - Social history → Patient properties (smoking, alcohol)
    # - rawText and cancer_type → Encounter or Patient notes
    "Procedure": {
        "class": ":Procedure",
        "id_prefix": "proc",
        "properties": {
            "id": ":hasId",
            "type": ":hasProcedureType",
            "date": ":hasDate",
            "details": ":hasDetails"
        },
        "relations": {
            "subject": ":procedureFor"
        }
    },
    "FamilyMemberHistory": {
        "class": ":FamilyMemberHistory",
        "id_prefix": "fh",
        "properties": {
            "id": ":hasId",
            "relative": ":hasRelative",
            "condition": ":hasCondition",
            "ageAtDiagnosis": ":hasAgeAtDiagnosis",
            "lynchSyndrome": ":hasLynchSyndrome"
        },
        "relations": {
            "patient": ":familyHistoryFor"
        }
    }
}


from rdflib import Graph, Namespace, Literal, RDF, URIRef
import uuid

# Namespaces
EX = Namespace("http://example.org/onto/colorectal#")
FHIR = Namespace("http://hl7.org/fhir/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

def new_individual(prefix):
    return EX[f"{prefix}-{uuid.uuid4().hex[:8]}"]

def add_data_property(g, subj, prop, value):
    if value is not None:
        g.add((subj, EX[prop], Literal(value)))

def convert_fhir_to_ontology(bundle):
    g = Graph()
    g.bind("ex", EX)

    # Step through FHIR entries
    entry_map = {}  # Keep track of FHIR ID → OWL individual

    for entry in bundle.get("entry", []):
        res = entry["resource"]
        rtype = res["resourceType"]

        # ----------------------- PATIENT -----------------------
        if rtype == "Patient":
            ind = new_individual("patient")
            entry_map[res["id"]] = ind
            g.add((ind, RDF.type, EX.Patient))

            if "gender" in res:
                add_data_property(g, ind, "hasSex", res["gender"])
            if "birthDate" in res:
                add_data_property(g, ind, "hasDOB", res["birthDate"])

        # ----------------------- OBSERVATION -----------------------
        elif rtype == "Observation":
            code = res["code"]["text"]
            obs_id = new_individual("obs")
            entry_map[res["id"]] = obs_id

            # Map code to class
            class_map = {
                "Faecal Immunochemical Test": EX.FIT_Result,
                "Haemoglobin": EX.Haemoglobin_Result,
                "Ferritin": EX.Ferritin_Result,
                "Mean Corpuscular Volume": EX.MCV_Result,
                "Creatinine": EX.Creatinine_Result,
                "Estimated Glomerular Filtration Rate": EX.eGFR_Result,
                "Tissue Transglutaminase Antibodies": EX.Coeliac_TTG_Result,
            }

            g.add((obs_id, RDF.type, class_map.get(code, EX.Observation)))

            # Set numeric value
            if "valueQuantity" in res:
                val = res["valueQuantity"].get("value")
                unit = res["valueQuantity"].get("unit")
                add_data_property(g, obs_id, "hasNumericValue", val)
                add_data_property(g, obs_id, "hasUnit", unit)

            # Interpretation
            if "interpretation" in res:
                interp = res["interpretation"]["text"]
                add_data_property(g, obs_id, "hasInterpretation", interp)

            # Link to patient
            subj_ref = res.get("subject", {}).get("reference")
            if subj_ref:
                fhir_id = subj_ref.split("/")[-1]
                if fhir_id in entry_map:
                    g.add((obs_id, EX.observedFor, entry_map[fhir_id]))

        # ----------------------- CONDITION -----------------------
        elif rtype == "Condition":
            cond_id = new_individual("cond")
            entry_map[res["id"]] = cond_id

            # Handle both FHIR format (code.text) and canonical format (code field)
            code = None
            if "code" in res:
                if isinstance(res["code"], dict) and "text" in res["code"]:
                    code = res["code"]["text"]
                elif isinstance(res["code"], str):
                    code = res["code"]
            
            # Map code to class - handle both display names and code values
            cond_map = {
                # Display names (FHIR format)
                "Change in bowel habit": EX.ChangeInBowelHabit,
                "Unintentional weight loss": EX.UnintentionalWeightLoss,
                "Rectal bleeding": EX.RectalBleeding,
                "Iron deficiency anaemia": EX.IronDeficiencyAnaemia,
                "Anal mass": EX.AnalMass,
                "Rectal mass": EX.RectalMass,
                "Abdominal mass": EX.AbdominalMass,
                "Family history of colorectal cancer": EX.FamilyHistoryOfColorectalCancer,
                # Code values (canonical format)
                "changeInBowelHabit": EX.ChangeInBowelHabit,
                "unintentionalWeightLoss": EX.UnintentionalWeightLoss,
                "rectalBleeding": EX.RectalBleeding,
                "ironDeficiencyAnaemia": EX.IronDeficiencyAnaemia,
                "analMass": EX.AnalMass,
                "rectalMass": EX.RectalMass,
                "abdominalMass": EX.AbdominalMass,
                "familyHistoryOfColorectalCancer": EX.FamilyHistoryOfColorectalCancer,
            }

            g.add((cond_id, RDF.type, cond_map.get(code, EX.Condition)))
            
            # Add properties if available (canonical format)
            if "display" in res:
                add_data_property(g, cond_id, "hasDisplay", res["display"])
            if "present" in res:
                add_data_property(g, cond_id, "hasPresent", res["present"])
            if "id" in res:
                add_data_property(g, cond_id, "hasId", res["id"])

            subj_ref = res.get("subject", {}).get("reference")
            if subj_ref:
                pid = subj_ref.split("/")[-1]
                if pid in entry_map:
                    g.add((cond_id, EX.affects, entry_map[pid]))

        # ----------------------- MEDICATION -----------------------
        elif rtype == "MedicationStatement":
            med_id = new_individual("med")
            entry_map[res["id"]] = med_id
            g.add((med_id, RDF.type, EX.Medication))
            
            med_name = res["medicationCodeableConcept"]["text"]
            add_data_property(g, med_id, "hasMedicationName", med_name)

            subj_ref = res["subject"]["reference"].split("/")[-1]
            if subj_ref in entry_map:
                g.add((med_id, EX.forPatient, entry_map[subj_ref]))
    
    return g


def convert_canonical_to_ontology(canonical):
    """Convert canonical JSON format directly to OWL ontology."""
    g = Graph()
    g.bind("ex", EX)
    
    entry_map = {}  # Keep track of IDs → OWL individuals
    patient_id = None
    
    # ----------------------- PATIENT -----------------------
    if "patient" in canonical:
        pat = canonical["patient"]
        patient_id = new_individual("patient")
        entry_map["patient"] = patient_id
        g.add((patient_id, RDF.type, EX.Patient))
        
        map_config = FHIR_TO_OWL_MAP["Patient"]
        for prop, owl_prop in map_config["properties"].items():
            if "." in prop:
                # Handle nested properties like contact.mobile
                parts = prop.split(".")
                value = pat
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                if value:
                    add_data_property(g, patient_id, owl_prop.replace(":", ""), value)
            elif prop in pat and pat[prop]:
                add_data_property(g, patient_id, owl_prop.replace(":", ""), pat[prop])
    
    # ----------------------- ORGANIZATION -----------------------
    if "organization" in canonical:
        org = canonical["organization"]
        org_id = new_individual("org")
        entry_map["organization"] = org_id
        g.add((org_id, RDF.type, EX.Organization))
        
        map_config = FHIR_TO_OWL_MAP["Organization"]
        for prop, owl_prop in map_config["properties"].items():
            if prop in org and org[prop]:
                add_data_property(g, org_id, owl_prop.replace(":", ""), org[prop])
    
    # ----------------------- ENCOUNTER -----------------------
    if "encounter" in canonical:
        enc = canonical["encounter"]
        enc_id = new_individual("enc")
        entry_map["encounter"] = enc_id
        g.add((enc_id, RDF.type, EX.Encounter))
        
        map_config = FHIR_TO_OWL_MAP["Encounter"]
        for prop, owl_prop in map_config["properties"].items():
            if prop in enc and enc[prop]:
                add_data_property(g, enc_id, owl_prop.replace(":", ""), enc[prop])
        
        if patient_id:
            g.add((enc_id, EX.encounterFor, patient_id))
    
    # ----------------------- REFERRAL -----------------------
    if "referral" in canonical:
        ref = canonical["referral"]
        ref_id = new_individual("ref")
        entry_map["referral"] = ref_id
        g.add((ref_id, RDF.type, EX.Referral))
        
        map_config = FHIR_TO_OWL_MAP["Referral"]
        for prop, owl_prop in map_config["properties"].items():
            if prop in ref and ref[prop]:
                add_data_property(g, ref_id, owl_prop.replace(":", ""), ref[prop])
        
        if patient_id:
            g.add((ref_id, EX.referralFor, patient_id))
    
    # ----------------------- OBSERVATIONS -----------------------
    if "observations" in canonical:
        map_config = FHIR_TO_OWL_MAP["Observation"]
        class_map = {k: getattr(EX, v.replace(":", "")) for k, v in map_config["class_map"].items()}
        
        for obs in canonical["observations"]:
            obs_id = new_individual("obs")
            if "id" in obs:
                entry_map[obs["id"]] = obs_id
            
            # Map code to class
            code = obs.get("code", "")
            obs_class = class_map.get(code, EX.Observation)
            g.add((obs_id, RDF.type, obs_class))
            
            # Add properties
            for prop, owl_prop in map_config["properties"].items():
                if prop in obs and obs[prop]:
                    add_data_property(g, obs_id, owl_prop.replace(":", ""), obs[prop])
            
            # Link to patient
            if patient_id:
                g.add((obs_id, EX.observedFor, patient_id))
    
    # ----------------------- CONDITIONS -----------------------
    if "conditions" in canonical:
        map_config = FHIR_TO_OWL_MAP["Condition"]
        class_map = {k: getattr(EX, v.replace(":", "")) for k, v in map_config["class_map"].items()}
        
        for cond in canonical["conditions"]:
            # Only process conditions where present is true
            if cond.get("present", "").lower() != "true":
                continue
            
            cond_id = new_individual("cond")
            if "id" in cond:
                entry_map[cond["id"]] = cond_id
            
            # Map code to class
            code = cond.get("code", "")
            cond_class = class_map.get(code, EX.Condition)
            g.add((cond_id, RDF.type, cond_class))
            
            # Add properties
            for prop, owl_prop in map_config["properties"].items():
                if prop in cond:
                    value = cond[prop]
                    # Only skip if value is None or empty string
                    if value is not None and value != "":
                        add_data_property(g, cond_id, owl_prop.replace(":", ""), value)
            
            # Link to patient
            if patient_id:
                g.add((cond_id, EX.affects, patient_id))
    
    # ----------------------- MEDICATIONS -----------------------
    if "medications" in canonical:
        map_config = FHIR_TO_OWL_MAP["Medication"]
        
        for med in canonical["medications"]:
            med_id = new_individual("med")
            if "id" in med:
                entry_map[med["id"]] = med_id
            
            g.add((med_id, RDF.type, EX.Medication))
            
            # Add properties
            for prop, owl_prop in map_config["properties"].items():
                if prop in med and med[prop]:
                    add_data_property(g, med_id, owl_prop.replace(":", ""), med[prop])
            
            # Link to patient
            if patient_id:
                g.add((med_id, EX.forPatient, patient_id))
    
    # ----------------------- ALLERGIES -----------------------
    if "allergies" in canonical:
        map_config = FHIR_TO_OWL_MAP["Allergy"]
        
        for alg in canonical["allergies"]:
            alg_id = new_individual("alg")
            if "id" in alg:
                entry_map[alg["id"]] = alg_id
            
            g.add((alg_id, RDF.type, EX.AllergyIntolerance))
            
            # Add properties
            for prop, owl_prop in map_config["properties"].items():
                if prop in alg and alg[prop]:
                    add_data_property(g, alg_id, owl_prop.replace(":", ""), alg[prop])
            
            # Link to patient
            if patient_id:
                g.add((alg_id, EX.allergyFor, patient_id))
    
    # ----------------------- INVESTIGATIONS -----------------------
    # Map investigations to Observation resources (FHIR)
    if "investigations" in canonical:
        inv = canonical["investigations"]
        map_config = FHIR_TO_OWL_MAP["Observation"]
        class_map = {k: getattr(EX, v.replace(":", "")) for k, v in map_config["class_map"].items()}
        
        # Urine Dipstick investigation
        if "urineDipstick" in inv:
            ud = inv["urineDipstick"]
            if ud.get("done", "").lower() == "true":
                obs_id = new_individual("obs")
                entry_map["inv-urineDipstick"] = obs_id
                
                # Map to UrineDipstick_Result observation
                obs_class = class_map.get("urineDipstick", EX.Observation)
                g.add((obs_id, RDF.type, obs_class))
                
                add_data_property(g, obs_id, "hasCode", "urineDipstick")
                add_data_property(g, obs_id, "hasDisplay", "Urine dipstick")
                if ud.get("result"):
                    add_data_property(g, obs_id, "hasStatus", ud["result"])
                if ud.get("date"):
                    add_data_property(g, obs_id, "hasDate", ud["date"])
                
                if patient_id:
                    g.add((obs_id, EX.observedFor, patient_id))
        
        # Coeliac Screen investigation
        if "coeliacScreen" in inv:
            cs = inv["coeliacScreen"]
            if cs.get("done", "").lower() == "true":
                obs_id = new_individual("obs")
                entry_map["inv-coeliacScreen"] = obs_id
                
                # Map to Coeliac_TTG_Result observation
                obs_class = class_map.get("ttg", EX.Observation)
                g.add((obs_id, RDF.type, obs_class))
                
                add_data_property(g, obs_id, "hasCode", "ttg")
                add_data_property(g, obs_id, "hasDisplay", "Coeliac screen (TTG)")
                if cs.get("ttgValue"):
                    add_data_property(g, obs_id, "hasNumericValue", cs["ttgValue"])
                if cs.get("ttgUnit"):
                    add_data_property(g, obs_id, "hasUnit", cs["ttgUnit"])
                if cs.get("result"):
                    add_data_property(g, obs_id, "hasStatus", cs["result"])
                if cs.get("date"):
                    add_data_property(g, obs_id, "hasDate", cs["date"])
                
                if patient_id:
                    g.add((obs_id, EX.observedFor, patient_id))
        
        # Iron Treatment investigation (status/plan, not an observation)
        # This could be a Procedure or MedicationRequest, but for now we'll skip it
        # or create it as a separate resource if needed
    
    # ----------------------- HISTORY -----------------------
    # Map history items to appropriate FHIR resources
    if "history" in canonical:
        hist = canonical["history"]
        
        # Medical history → Condition resources (with status)
        if "medical" in hist:
            for med_hx in hist["medical"]:
                cond_id = new_individual("cond")
                if "id" in med_hx:
                    entry_map[med_hx["id"]] = cond_id
                
                # Medical history conditions are Condition resources
                g.add((cond_id, RDF.type, EX.Condition))
                
                # Add properties
                if "code" in med_hx:
                    add_data_property(g, cond_id, "hasCode", med_hx["code"])
                if "display" in med_hx:
                    add_data_property(g, cond_id, "hasDisplay", med_hx["display"])
                if "status" in med_hx:
                    # Status indicates if condition is active or historical
                    status = med_hx["status"]
                    add_data_property(g, cond_id, "hasStatus", status)
                    # Link to patient if active or historical (both are relevant)
                    if patient_id:
                        g.add((cond_id, EX.affects, patient_id))
        
        # Procedures → Procedure resources
        if "procedures" in hist:
            map_config = FHIR_TO_OWL_MAP["Procedure"]
            for proc in hist["procedures"]:
                proc_id = new_individual("proc")
                if "id" in proc:
                    entry_map[proc["id"]] = proc_id
                
                g.add((proc_id, RDF.type, EX.Procedure))
                
                # Add properties
                for prop, owl_prop in map_config["properties"].items():
                    if prop in proc and proc[prop]:
                        add_data_property(g, proc_id, owl_prop.replace(":", ""), proc[prop])
                
                # Link to patient
                if patient_id:
                    g.add((proc_id, EX.procedureFor, patient_id))
        
        # Family history → FamilyMemberHistory resources
        if "family" in hist:
            map_config = FHIR_TO_OWL_MAP["FamilyMemberHistory"]
            for fh in hist["family"]:
                fh_id = new_individual("fh")
                if "id" in fh:
                    entry_map[fh["id"]] = fh_id
                
                g.add((fh_id, RDF.type, EX.FamilyMemberHistory))
                
                # Add properties
                for prop, owl_prop in map_config["properties"].items():
                    if prop in fh and fh[prop]:
                        add_data_property(g, fh_id, owl_prop.replace(":", ""), fh[prop])
                
                # Link to patient
                if patient_id:
                    g.add((fh_id, EX.familyHistoryFor, patient_id))
        
        # Social history → Patient properties
        if "social" in hist and patient_id:
            social = hist["social"]
            if "smokingStatus" in social and social["smokingStatus"]:
                add_data_property(g, patient_id, "hasSmokingStatus", social["smokingStatus"])
            if "alcoholUnitsPerWeek" in social and social["alcoholUnitsPerWeek"]:
                add_data_property(g, patient_id, "hasAlcoholUnitsPerWeek", social["alcoholUnitsPerWeek"])
            if "alcoholPattern" in social and social["alcoholPattern"]:
                add_data_property(g, patient_id, "hasAlcoholPattern", social["alcoholPattern"])
    
    # Raw text and cancer type → Add to Encounter or as Patient notes
    if "rawText" in canonical and canonical["rawText"]:
        # Add to encounter if it exists, otherwise to patient
        if "encounter" in entry_map:
            add_data_property(g, entry_map["encounter"], "hasRawText", canonical["rawText"])
        elif patient_id:
            add_data_property(g, patient_id, "hasRawText", canonical["rawText"])
    
    if "cancer_type" in canonical and canonical["cancer_type"]:
        # Add to encounter or patient
        if "encounter" in entry_map:
            add_data_property(g, entry_map["encounter"], "hasCancerType", canonical["cancer_type"])
        elif patient_id:
            add_data_property(g, patient_id, "hasCancerType", canonical["cancer_type"])
    
    return g


# Load canonical JSON and convert to OWL
import json

with open('canonical.json', 'r') as f:
    canonical = json.load(f)

g = convert_canonical_to_ontology(canonical)
# print(g.serialize(format="turtle"))

