from copy import deepcopy
from typing import Any, Dict, List, Optional

# --- UK Core / FHIR profile URLs (yours) ---

PATIENT_PROFILE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Patient"
ENCOUNTER_PROFILE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Encounter"
ORGANIZATION_PROFILE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
SERVICE_REQUEST_PROFILE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-ServiceRequest"
CARE_PLAN_PROFILE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-CarePlan"
GUIDANCE_RESPONSE_PROFILE = "http://hl7.org/fhir/StructureDefinition/GuidanceResponse"

OBSERVATION_PROFILE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Observation"
CONDITION_PROFILE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Condition"
MEDICATION_STATEMENT_PROFILE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-MedicationStatement"
ALLERGY_PROFILE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-AllergyIntolerance"
ALCOHOL_INTAKE_PROFILE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Observation-AlcoholConsumption"
VITAL_SIGNS_BODY_WEIGHT_PROFILE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Observation-VitalSigns-BodyWeight"
FAMILY_MEMBER_HISTORY_PROFILE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-FamilyMemberHistory"


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

class IdGenerator:
    """Simple ID generator to keep references consistent."""
    def __init__(self):
        self.counters = {}

    def new(self, prefix: str) -> str:
        self.counters.setdefault(prefix, 0)
        self.counters[prefix] += 1
        return f"{prefix}-{self.counters[prefix]}"


def add_entry(bundle: Dict[str, Any], resource: Dict[str, Any]) -> None:
    """Append a FHIR resource into the bundle with a urn:uuid fullUrl."""
    full_url = f"urn:uuid:{resource['id']}"
    bundle.setdefault("entry", []).append({
        "fullUrl": full_url,
        "resource": resource,
    })


def safe_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    return None


# -------------------------------------------------------------------
# Main conversion function
# -------------------------------------------------------------------

def canonical_to_fhir_bundle(canonical: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert your canonical triage JSON into a UK Core FHIR R4 Bundle.

    Expected canonical structure:
      - patient
      - organization
      - encounter
      - referral
      - observations (list)
      - conditions (list)
      - medications (list)
      - allergies (list)
      - investigations (urineDipstick, coeliacScreen, ironTreatment)
      - history (medical, procedures, family, social, rawText)
      - (optionally) triage
    """
    ids = IdGenerator()
    bundle: Dict[str, Any] = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": []
    }

    # ----------------------------------------------------------------
    # Patient
    # ----------------------------------------------------------------
    patient_data = canonical.get("patient", {}) or {}
    patient_id = ids.new("patient")

    patient_res = {
        "resourceType": "Patient",
        "id": patient_id,
        "meta": {"profile": [PATIENT_PROFILE]},
    }

    # Demographics
    sex = patient_data.get("sex")
    if sex:
        patient_res["gender"] = sex

    dob = patient_data.get("dob")
    if dob:
        patient_res["birthDate"] = dob

    name = patient_data.get("name")
    if name:
        patient_res["name"] = [{"text": name}]

    address = patient_data.get("address")
    if address:
        patient_res["address"] = [{"text": address}]

    identifiers = []
    if patient_data.get("nhsNumber"):
        identifiers.append({
            "system": "https://fhir.nhs.uk/Id/nhs-number",
            "value": patient_data["nhsNumber"]
        })
    if patient_data.get("hospitalNumber"):
        identifiers.append({
            "system": "https://example.org/hospital-number",
            "value": patient_data["hospitalNumber"]
        })
    if identifiers:
        patient_res["identifier"] = identifiers

    # Contact
    contact = patient_data.get("contact") or {}
    telecom = []
    if contact.get("mobile"):
        telecom.append({"system": "phone", "use": "mobile", "value": contact["mobile"]})
    if contact.get("landline"):
        telecom.append({"system": "phone", "use": "home", "value": contact["landline"]})
    if contact.get("email"):
        telecom.append({"system": "email", "value": contact["email"]})
    if telecom:
        patient_res["telecom"] = telecom

    add_entry(bundle, patient_res)

    # ----------------------------------------------------------------
    # Organization (referring org / practice)
    # ----------------------------------------------------------------
    org_data = canonical.get("organization") or {}
    if any(org_data.values()):
        org_id = ids.new("org")
        org_res = {
            "resourceType": "Organization",
            "id": org_id,
            "meta": {"profile": [ORGANIZATION_PROFILE]},
        }
        if org_data.get("name"):
            org_res["name"] = org_data["name"]

        telecom = []
        if org_data.get("telephone"):
            telecom.append({"system": "phone", "value": org_data["telephone"]})
        if org_data.get("fax"):
            telecom.append({"system": "fax", "value": org_data["fax"]})
        if org_data.get("email"):
            telecom.append({"system": "email", "value": org_data["email"]})
        if telecom:
            org_res["telecom"] = telecom

        if org_data.get("odsCode"):
            org_res["identifier"] = [{
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": org_data["odsCode"]
            }]

        add_entry(bundle, org_res)
    else:
        org_id = None

    # ----------------------------------------------------------------
    # Encounter
    # ----------------------------------------------------------------
    enc_data = canonical.get("encounter") or {}
    enc_id = ids.new("encounter")
    encounter_res = {
        "resourceType": "Encounter",
        "id": enc_id,
        "meta": {"profile": [ENCOUNTER_PROFILE]},
        "status": "finished",  # could be "in-progress" if you prefer
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "AMB",
            "display": "ambulatory"
        },
        "subject": {"reference": f"Patient/{patient_id}"}
    }

    if enc_data.get("date"):
        encounter_res["period"] = {"start": enc_data["date"]}

    if enc_data.get("reason"):
        encounter_res["reasonCode"] = [{"text": enc_data["reason"]}]

    # WHO performance status as extension (simple approach)
    if enc_data.get("whoPerformanceStatus") is not None:
        encounter_res.setdefault("extension", []).append({
            "url": "http://example.org/fhir/StructureDefinition/who-performance-status",
            "valueInteger": enc_data["whoPerformanceStatus"]
        })

    add_entry(bundle, encounter_res)

    # ----------------------------------------------------------------
    # ServiceRequest (referral)
    # ----------------------------------------------------------------
    ref_data = canonical.get("referral") or {}
    sr_id = ids.new("sr")
    service_request = {
      "resourceType": "ServiceRequest",
      "id": sr_id,
      "meta": {"profile": [SERVICE_REQUEST_PROFILE]},
      "status": "active",
      "intent": "order",
      "subject": {"reference": f"Patient/{patient_id}"},
      "encounter": {"reference": f"Encounter/{enc_id}"},
    }

    if ref_data.get("priority"):
        service_request["priority"] = ref_data["priority"]
    if ref_data.get("service"):
        service_request["code"] = {"text": ref_data["service"]}
    if ref_data.get("dateOfReferral"):
        service_request["authoredOn"] = ref_data["dateOfReferral"]

    add_entry(bundle, service_request)

    # ----------------------------------------------------------------
    # Observations (canonical.observations list)
    # ----------------------------------------------------------------
    for obs in canonical.get("observations") or []:
        obs_id = ids.new("obs")
        fhir_obs = {
            "resourceType": "Observation",
            "id": obs_id,
            "meta": {"profile": [OBSERVATION_PROFILE]},
            "status": "final",
            "code": {"text": obs.get("display") or obs.get("code") or "Observation"},
            "subject": {"reference": f"Patient/{patient_id}"},
            "encounter": {"reference": f"Encounter/{enc_id}"}
        }

        if obs.get("date"):
            fhir_obs["effectiveDateTime"] = obs["date"]

        value = obs.get("value")
        unit = obs.get("unit")
        if value is not None:
            fhir_obs["valueQuantity"] = {
                "value": value,
                "unit": unit or "",
                "system": "http://unitsofmeasure.org"
            }

        status = obs.get("status")
        if status:
            fhir_obs["interpretation"] = {"text": status}

        add_entry(bundle, fhir_obs)

    # ----------------------------------------------------------------
    # Investigations block → additional Observations / MedicationStatement
    # ----------------------------------------------------------------
    inv = canonical.get("investigations") or {}

    # Urine dipstick
    urine = inv.get("urineDipstick") or {}
    if urine.get("done") is True:
        obs_id = ids.new("obs-urine")
        fhir_urine = {
            "resourceType": "Observation",
            "id": obs_id,
            "meta": {"profile": [OBSERVATION_PROFILE]},
            "status": "final",
            "code": {"text": "Urine dipstick"},
            "subject": {"reference": f"Patient/{patient_id}"},
            "encounter": {"reference": f"Encounter/{enc_id}"}
        }
        if urine.get("date"):
            fhir_urine["effectiveDateTime"] = urine["date"]
        if urine.get("result"):
            fhir_urine["interpretation"] = {"text": urine["result"]}
        add_entry(bundle, fhir_urine)

    # Coeliac screen (TTG)
    coeliac = inv.get("coeliacScreen") or {}
    if coeliac.get("done") is True:
        obs_id = ids.new("obs-ttg")
        fhir_ttg = {
            "resourceType": "Observation",
            "id": obs_id,
            "meta": {"profile": [OBSERVATION_PROFILE]},
            "status": "final",
            "code": {"text": "Coeliac screen (TTG)"},
            "subject": {"reference": f"Patient/{patient_id}"},
            "encounter": {"reference": f"Encounter/{enc_id}"}
        }
        if coeliac.get("date"):
            fhir_ttg["effectiveDateTime"] = coeliac["date"]

        if coeliac.get("ttgValue") is not None:
            fhir_ttg["valueQuantity"] = {
                "value": coeliac["ttgValue"],
                "unit": coeliac.get("ttgUnit") or "",
                "system": "http://unitsofmeasure.org"
            }

        if coeliac.get("result"):
            fhir_ttg["interpretation"] = {"text": coeliac["result"]}

        add_entry(bundle, fhir_ttg)

    # Iron treatment started → MedicationStatement
    iron_treat = inv.get("ironTreatment") or {}
    if iron_treat.get("started") is True:
        med_id = ids.new("med-iron")
        med_stmt = {
            "resourceType": "MedicationStatement",
            "id": med_id,
            "meta": {"profile": [MEDICATION_STATEMENT_PROFILE]},
            "status": "active",
            "medicationCodeableConcept": {
                "text": iron_treat.get("notes") or "Oral iron"
            },
            "subject": {"reference": f"Patient/{patient_id}"}
        }
        if iron_treat.get("startDate"):
            med_stmt["effectiveDateTime"] = iron_treat["startDate"]
        add_entry(bundle, med_stmt)

    # ----------------------------------------------------------------
    # Conditions
    # ----------------------------------------------------------------
    for cond in canonical.get("conditions") or []:
        if cond.get("present") is not True:
            continue
        cond_id = ids.new("cond")
        fhir_cond = {
            "resourceType": "Condition",
            "id": cond_id,
            "meta": {"profile": [CONDITION_PROFILE]},
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active"
                }]
            },
            "code": {"text": cond.get("display") or cond.get("code") or "Condition"},
            "subject": {"reference": f"Patient/{patient_id}"}
        }
        add_entry(bundle, fhir_cond)

    # ----------------------------------------------------------------
    # Medications
    # ----------------------------------------------------------------
    for med in canonical.get("medications") or []:
        if not med.get("name"):
            continue
        med_id = ids.new("med")
        med_stmt = {
            "resourceType": "MedicationStatement",
            "id": med_id,
            "meta": {"profile": [MEDICATION_STATEMENT_PROFILE]},
            "status": med.get("status") or "active",
            "medicationCodeableConcept": {"text": med["name"]},
            "subject": {"reference": f"Patient/{patient_id}"}
        }
        add_entry(bundle, med_stmt)

    # ----------------------------------------------------------------
    # Allergies
    # ----------------------------------------------------------------
    for alg in canonical.get("allergies") or []:
        if not alg.get("substance"):
            continue
        alg_id = ids.new("alg")
        allergy_res = {
            "resourceType": "AllergyIntolerance",
            "id": alg_id,
            "meta": {"profile": [ALLERGY_PROFILE]},
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                    "code": "active"
                }]
            },
            "code": {"text": alg["substance"]},
            "patient": {"reference": f"Patient/{patient_id}"}
        }
        if alg.get("reaction"):
            allergy_res["reaction"] = [{"description": alg["reaction"]}]
        add_entry(bundle, allergy_res)

    # ----------------------------------------------------------------
    # Family history
    # ----------------------------------------------------------------
    history = canonical.get("history") or {}
    for fh in history.get("family") or []:
        if not fh.get("relative") and not fh.get("condition"):
            continue
        fh_id = ids.new("fhx")
        fhx_res = {
            "resourceType": "FamilyMemberHistory",
            "id": fh_id,
            "meta": {"profile": [FAMILY_MEMBER_HISTORY_PROFILE]},
            "status": "completed",
            "patient": {"reference": f"Patient/{patient_id}"},
            "relationship": {"text": fh.get("relative") or "relative"},
            "condition": [{
                "code": {"text": fh.get("condition") or "condition"}
            }]
        }
        age = fh.get("ageAtDiagnosis")
        if age is not None:
            fhx_res["condition"][0]["onsetAge"] = {
                "value": age,
                "unit": "years"
            }
        add_entry(bundle, fhx_res)

    # ----------------------------------------------------------------
    # OPTIONAL: triage → GuidanceResponse / CarePlan
    # (only create if something is actually populated)
    # ----------------------------------------------------------------
    triage = canonical.get("triage") or {}
    if triage.get("decisionCode") or triage.get("decisionText"):
        # CarePlan as recommended actions
        cp_id = ids.new("careplan")
        activities = []
        for act in triage.get("recommendedActions") or []:
            activities.append({
                "detail": {
                    "kind": "ServiceRequest",
                    "code": {"text": act},
                    "status": "not-started"
                }
            })

        careplan_res = {
            "resourceType": "CarePlan",
            "id": cp_id,
            "meta": {"profile": [CARE_PLAN_PROFILE]},
            "status": "active",
            "intent": "plan",
            "subject": {"reference": f"Patient/{patient_id}"},
            "encounter": {"reference": f"Encounter/{enc_id}"},
            "title": triage.get("decisionCode") or "Triage care plan",
            "description": triage.get("decisionText") or None,
            "activity": activities
        }
        # Remove description if None
        if careplan_res.get("description") is None:
            careplan_res.pop("description")
        add_entry(bundle, careplan_res)

        # GuidanceResponse summarising decision
        gr_id = ids.new("guidance")
        guidance_res = {
            "resourceType": "GuidanceResponse",
            "id": gr_id,
            "meta": {"profile": [GUIDANCE_RESPONSE_PROFILE]},
            "status": "success",
            "subject": {"reference": f"Patient/{patient_id}"},
            "encounter": {"reference": f"Encounter/{enc_id}"},
            "result": {"reference": f"CarePlan/{cp_id}"},
        }

        reason_texts = triage.get("criteriaMatched") or []
        if reason_texts:
            guidance_res["reasonCode"] = [{"text": "; ".join(reason_texts)}]

        add_entry(bundle, guidance_res)

    return bundle

canonical = {"patient":{"id":"" ,"name":"" ,"sex":"female","dob":"" ,"ethnicity":"" ,"language":"" ,"hospitalNumber":"" ,"address":"" ,"nhsNumber":"" ,"contact":{"mobile":"" ,"landline":"" ,"email":"" }},"organization":{"id":"" ,"name":"" ,"odsCode":"" ,"telephone":"" ,"fax":"" ,"email":"" },"encounter":{"id":"" ,"date":"" ,"reason":"Urgent two-week-wait colorectal referral for persistent change in bowel habit, weight loss, positive FIT","location":"" ,"interpreterRequired":"false","capacityToConsent":"true","whoPerformanceStatus":"1"},"referral":{"id":"" ,"service":"Colorectal two-week-wait (urgent cancer pathway)","priority":"urgent","referrerName":"" ,"practiceName":"" ,"dateOfDecisionToRefer":"" ,"dateOfReferral":"" ,"consentToText":"" ,"gpDeclaration":"" },"observations":[{"id":"obs-fit","code":"fit","display":"Faecal immunochemical test","value":"142","unit":"µg Hb/g","date":"" ,"status":"final"},{"id":"obs-hb","code":"hb","display":"Haemoglobin","value":"103","unit":"g/L","date":"" ,"status":"final"},{"id":"obs-ferritin","code":"ferritin","display":"Ferritin","value":"18","unit":"µg/L","date":"" ,"status":"final"},{"id":"obs-mcv","code":"mcv","display":"Mean corpuscular volume","value":"74","unit":"fL","date":"" ,"status":"final"},{"id":"obs-ttg","code":"ttg","display":"Tissue transglutaminase antibody","value":"0","unit":"","date":"" ,"status":"negative"},{"id":"obs-creatinine","code":"creatinine","display":"Creatinine","value":"78","unit":"µmol/L","date":"" ,"status":"final"},{"id":"obs-egfr","code":"egfr","display":"Estimated GFR","value":"74","unit":"ml/min/1.73 m²","date":"" ,"status":"final"},{"id":"obs-urine-dip","code":"urineDipstick","display":"Urine dipstick","value":"","unit":"","date":"" ,"status":"normal"}],"conditions":[{"id":"cond-change-bowel","code":"changeInBowelHabit","display":"Change in bowel habit","present":"true"},{"id":"cond-rectal-bleeding","code":"rectalBleeding","display":"Rectal bleeding","present":"true"},{"id":"cond-anal-mass","code":"analMass","display":"Anal mass","present":"false"},{"id":"cond-rectal-mass","code":"rectalMass","display":"Rectal mass","present":"false"},{"id":"cond-ida","code":"ironDeficiencyAnaemia","display":"Iron deficiency anaemia","present":"true"},{"id":"cond-weight-loss","code":"unintentionalWeightLoss","display":"Unintentional weight loss","present":"true"},{"id":"cond-abdo-mass","code":"abdominalMass","display":"Abdominal mass","present":"false"},{"id":"cond-fh-crc","code":"familyHistoryOfColorectalCancer","display":"Family history of colorectal cancer","present":"true"}],"medications":[{"id":"med1","name":"Metformin","doseText":"","status":"active"},{"id":"med2","name":"Ramipril","doseText":"","status":"active"},{"id":"med3","name":"Levothyroxine","doseText":"","status":"active"},{"id":"med4","name":"Omeprazole","doseText":"","status":"active"},{"id":"med5","name":"Paracetamol","doseText":"PRN","status":"active"}],"allergies":[{"id":"alg1","substance":"Drug allergies","reaction":"","criticality":""}],"investigations":{"urineDipstick":{"done":"true","result":"normal","date":"" },"coeliacScreen":{"done":"true","ttgValue":"0","ttgUnit":"","result":"negative","date":"" },"ironTreatment":{"started":"false","startDate":"" ,"notes":"" }},"history":{"medical":[{"id":"hx1","code":"E11","display":"Type 2 diabetes mellitus","status":"active"},{"id":"hx2","code":"I10","display":"Hypertension","status":"active"},{"id":"hx3","code":"E03.9","display":"Hypothyroidism","status":"active"},{"id":"hx4","code":"K57.3","display":"Diverticular disease of sigmoid colon; prior diverticulitis episode 5 years ago","status":"historical"},{"id":"hx5","code":"M17","display":"Osteoarthritis of knees","status":"active"}],"procedures":[{"id":"proc1","type":"Colonoscopy","date":"","details":"10 years ago; diverticular disease only"}],"family":[{"id":"fh1","relative":"Brother","condition":"Colorectal cancer","ageAtDiagnosis":"62","lynchSyndrome":"possible"},{"id":"fh2","relative":"Mother","condition":"Endometrial cancer","ageAtDiagnosis":"","lynchSyndrome":"possible"}],"social":{"smokingStatus":"former (20 pack-years; quit 12 years ago)","alcoholUnitsPerWeek":"6-8","alcoholPattern":"" },"rawText":"68-year-old woman with 3 months of looser stools and urgency; intermittent dark red blood mixed with stool; FIT 142 µg Hb/g; Hb 103 g/L; Ferritin 18 µg/L; MCV 74 fL; Creatinine 78 µmol/L; eGFR 74 ml/min/1.73 m²; TTG negative; urine dipstick normal; weight loss ~6 kg over 4 months; reduced appetite and early satiety; PMH: T2DM, HTN, hypothyroidism, prior sigmoid diverticulitis; OA knees; colonoscopy 10 years ago showed diverticular disease only; FH: brother CRC at 62, mother endometrial cancer; former smoker 20 pack-years, quit 12 years ago; alcohol 6–8 units/week; meds: metformin, ramipril, levothyroxine, omeprazole, paracetamol PRN; no known drug allergies.","cancer_type":"colorectal"}}
bundle = canonical_to_fhir_bundle(canonical)
# Then JSON-serialise, validate, send to reasoner-conversion, etc.
print(bundle)