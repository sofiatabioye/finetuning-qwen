"""
Code mappings for converting user-friendly JSON codes to full FHIR ontology codes.
This module provides lookup tables for observations, conditions, medications, etc.
"""

# Observation code mappings (simple code → full SNOMED/LOINC)
OBSERVATION_CODES = {
    "fit": {
        "system": "http://snomed.info/sct",
        "code": "773530003",
        "display": "Faecal immunochemical test"
    },
    "hb": {
        "system": "http://loinc.org",
        "code": "718-7",
        "display": "Hemoglobin"
    },
    "haemoglobin": {
        "system": "http://loinc.org",
        "code": "718-7",
        "display": "Hemoglobin"
    },
    "ferritin": {
        "system": "http://loinc.org",
        "code": "2276-4",
        "display": "Ferritin"
    },
    "mcv": {
        "system": "http://loinc.org",
        "code": "787-2",
        "display": "MCV"
    },
    "creatinine": {
        "system": "http://loinc.org",
        "code": "2160-0",
        "display": "Creatinine"
    },
    "egfr": {
        "system": "http://loinc.org",
        "code": "33914-3",
        "display": "eGFR"
    },
    "ttg": {
        "system": "http://loinc.org",
        "code": "16125-7",
        "display": "tTG IgA"
    },
    "urineDipstick": {
        "system": "http://snomed.info/sct",
        "code": "271650006",
        "display": "Urine dipstick test"
    },
    "weight": {
        "system": "http://loinc.org",
        "code": "29463-7",
        "display": "Body weight"
    },
    "bodyWeight": {
        "system": "http://loinc.org",
        "code": "29463-7",
        "display": "Body weight"
    },
    "smokingStatus": {
        "system": "http://snomed.info/sct",
        "code": "365980008",
        "display": "Tobacco smoking status"
    },
    "alcoholUse": {
        "system": "http://snomed.info/sct",
        "code": "160573003",
        "display": "Alcohol consumption"
    },
    "alcohol": {
        "system": "http://snomed.info/sct",
        "code": "160573003",
        "display": "Alcohol consumption"
    }
}

# Condition code mappings (simple code → SNOMED)
CONDITION_CODES = {
    "changeInBowelHabit": {
        "system": "http://snomed.info/sct",
        "code": "62315008",
        "display": "Change in bowel habit"
    },
    "rectalBleeding": {
        "system": "http://snomed.info/sct",
        "code": "62315008",
        "display": "Rectal bleeding"
    },
    "unintentionalWeightLoss": {
        "system": "http://snomed.info/sct",
        "code": "161832001",
        "display": "Unintentional weight loss"
    },
    "diabetesType2": {
        "system": "http://snomed.info/sct",
        "code": "44054006",
        "display": "Diabetes mellitus type 2"
    },
    "hypertension": {
        "system": "http://snomed.info/sct",
        "code": "38341003",
        "display": "Hypertensive disorder"
    },
    "hypothyroidism": {
        "system": "http://snomed.info/sct",
        "code": "40930008",
        "display": "Hypothyroidism"
    },
    "diverticulitis": {
        "system": "http://snomed.info/sct",
        "code": "60468000",
        "display": "Diverticulitis of sigmoid colon"
    },
    "osteoarthritis": {
        "system": "http://snomed.info/sct",
        "code": "396275006",
        "display": "Osteoarthritis of knee"
    },
    "ironDeficiencyAnaemia": {
        "system": "http://snomed.info/sct",
        "code": "84094000",
        "display": "Iron deficiency anaemia"
    },
    "familyHistoryOfColorectalCancer": {
        "system": "http://snomed.info/sct",
        "code": "429268008",
        "display": "Family history of colorectal cancer"
    },
    "analMass": {
        "system": "http://snomed.info/sct",
        "code": "126906006",
        "display": "Anal mass"
    },
    "rectalMass": {
        "system": "http://snomed.info/sct",
        "code": "126906006",
        "display": "Rectal mass"
    },
    "abdominalMass": {
        "system": "http://snomed.info/sct",
        "code": "118330005",
        "display": "Abdominal mass"
    }
}

# Family history condition codes
FAMILY_CONDITION_CODES = {
    "colorectalCancer": {
        "system": "http://snomed.info/sct",
        "code": "363418001",
        "display": "Malignant neoplasm of colon"
    },
    "endometrialCancer": {
        "system": "http://snomed.info/sct",
        "code": "126906006",
        "display": "Malignant neoplasm of endometrium"
    },
    "breastCancer": {
        "system": "http://snomed.info/sct",
        "code": "254837009",
        "display": "Malignant neoplasm of breast"
    }
}

# Relationship code mappings
RELATIONSHIP_CODES = {
    "brother": {
        "system": "http://hl7.org/fhir/v3/RoleCode",
        "code": "BRO",
        "display": "brother"
    },
    "sister": {
        "system": "http://hl7.org/fhir/v3/RoleCode",
        "code": "SIS",
        "display": "sister"
    },
    "mother": {
        "system": "http://hl7.org/fhir/v3/RoleCode",
        "code": "MTH",
        "display": "mother"
    },
    "father": {
        "system": "http://hl7.org/fhir/v3/RoleCode",
        "code": "FTH",
        "display": "father"
    },
    "son": {
        "system": "http://hl7.org/fhir/v3/RoleCode",
        "code": "SON",
        "display": "son"
    },
    "daughter": {
        "system": "http://hl7.org/fhir/v3/RoleCode",
        "code": "DAU",
        "display": "daughter"
    }
}

# Medication name to code mappings (simplified - in practice, use RxNorm or SNOMED)
MEDICATION_CODES = {
    "metformin": {
        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "code": "6809",
        "display": "Metformin"
    },
    "ramipril": {
        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "code": "35208",
        "display": "Ramipril"
    },
    "levothyroxine": {
        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "code": "9663",
        "display": "Levothyroxine"
    },
    "omeprazole": {
        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "code": "7646",
        "display": "Omeprazole"
    },
    "paracetamol": {
        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "code": "161",
        "display": "Paracetamol"
    }
}

# Referral type mappings
REFERRAL_TYPE_CODES = {
    "colorectalSurgery": {
        "system": "http://snomed.info/sct",
        "code": "713400007",
        "display": "Referral to colorectal surgery"
    },
    "gastroenterology": {
        "system": "http://snomed.info/sct",
        "code": "183519008",
        "display": "Referral to gastroenterology"
    },
    "oncology": {
        "system": "http://snomed.info/sct",
        "code": "394576009",
        "display": "Referral to oncology"
    }
}

# Encounter type mappings
ENCOUNTER_TYPE_CODES = {
    "outpatient": {
        "system": "http://hl7.org/fhir/v3/ActCode",
        "code": "AMB",
        "display": "ambulatory"
    },
    "inpatient": {
        "system": "http://hl7.org/fhir/v3/ActCode",
        "code": "IMP",
        "display": "inpatient encounter"
    },
    "emergency": {
        "system": "http://hl7.org/fhir/v3/ActCode",
        "code": "EMER",
        "display": "emergency"
    }
}

# Practitioner role codes
PRACTITIONER_ROLE_CODES = {
    "generalPractitioner": {
        "system": "http://snomed.info/sct",
        "code": "62247001",
        "display": "General practitioner"
    },
    "consultant": {
        "system": "http://snomed.info/sct",
        "code": "304292004",
        "display": "Consultant"
    },
    "specialist": {
        "system": "http://snomed.info/sct",
        "code": "41904004",
        "display": "Specialist"
    },
    "nurse": {
        "system": "http://snomed.info/sct",
        "code": "106292003",
        "display": "Nurse"
    }
}

# Status mappings
CONDITION_STATUS_MAP = {
    "active": "active",
    "resolved": "resolved",
    "inactive": "inactive",
    "remission": "remission"
}

OBSERVATION_STATUS_MAP = {
    "final": "final",
    "preliminary": "preliminary",
    "amended": "amended",
    "cancelled": "cancelled"
}

MEDICATION_STATUS_MAP = {
    "active": "active",
    "stopped": "stopped",
    "completed": "completed",
    "on-hold": "on-hold"
}

REFERRAL_STATUS_MAP = {
    "active": "active",
    "completed": "completed",
    "cancelled": "cancelled",
    "draft": "draft"
}

# Smoking status codes
SMOKING_STATUS_CODES = {
    "never": {
        "system": "http://snomed.info/sct",
        "code": "266919005",
        "display": "Never smoked"
    },
    "current": {
        "system": "http://snomed.info/sct",
        "code": "77176002",
        "display": "Smoker"
    },
    "former": {
        "system": "http://snomed.info/sct",
        "code": "8517006",
        "display": "Former smoker"
    },
    "daily": {
        "system": "http://snomed.info/sct",
        "code": "449868002",
        "display": "Smokes tobacco daily"
    },
    "occasional": {
        "system": "http://snomed.info/sct",
        "code": "428041000124106",
        "display": "Occasional tobacco smoker"
    },
    "unknown": {
        "system": "http://snomed.info/sct",
        "code": "266927001",
        "display": "Tobacco smoking consumption unknown"
    },
    "heavy": {
        "system": "http://snomed.info/sct",
        "code": "230063004",
        "display": "Heavy cigarette smoker"
    },
    "light": {
        "system": "http://snomed.info/sct",
        "code": "230060001",
        "display": "Light cigarette smoker"
    }
}

# Allergy substance codes (common examples)
ALLERGY_SUBSTANCE_CODES = {
    "penicillin": {
        "system": "http://snomed.info/sct",
        "code": "373270004",
        "display": "Penicillin"
    },
    "aspirin": {
        "system": "http://snomed.info/sct",
        "code": "372912004",
        "display": "Aspirin"
    },
    "peanuts": {
        "system": "http://snomed.info/sct",
        "code": "762952008",
        "display": "Peanut"
    },
    "shellfish": {
        "system": "http://snomed.info/sct",
        "code": "227493005",
        "display": "Shellfish"
    }
}

# Allergy reaction manifestation codes
ALLERGY_REACTION_CODES = {
    "anaphylaxis": {
        "system": "http://snomed.info/sct",
        "code": "39579001",
        "display": "Anaphylaxis"
    },
    "urticaria": {
        "system": "http://snomed.info/sct",
        "code": "247472004",
        "display": "Urticaria"
    },
    "rash": {
        "system": "http://snomed.info/sct",
        "code": "271807003",
        "display": "Rash"
    },
    "angioedema": {
        "system": "http://snomed.info/sct",
        "code": "404640003",
        "display": "Angioedema"
    }
}

# Helper functions
def get_observation_code(simple_code: str) -> dict:
    """Get full observation code from simple code."""
    return OBSERVATION_CODES.get(simple_code.lower(), {
        "system": "http://snomed.info/sct",
        "code": simple_code,
        "display": simple_code
    })

def get_condition_code(simple_code: str) -> dict:
    """Get full condition code from simple code."""
    return CONDITION_CODES.get(simple_code, {
        "system": "http://snomed.info/sct",
        "code": simple_code,
        "display": simple_code
    })

def get_family_condition_code(simple_code: str) -> dict:
    """Get full family condition code from simple code."""
    return FAMILY_CONDITION_CODES.get(simple_code, {
        "system": "http://snomed.info/sct",
        "code": simple_code,
        "display": simple_code
    })

def get_relationship_code(relationship: str) -> dict:
    """Get full relationship code from simple relationship string."""
    return RELATIONSHIP_CODES.get(relationship.lower(), {
        "system": "http://hl7.org/fhir/v3/RoleCode",
        "code": relationship.upper(),
        "display": relationship
    })

def get_medication_code(medication_name: str) -> dict:
    """Get medication code from name."""
    return MEDICATION_CODES.get(medication_name.lower(), {
        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "code": medication_name,
        "display": medication_name
    })

def get_referral_type_code(simple_type: str) -> dict:
    """Get referral type code from simple type string."""
    return REFERRAL_TYPE_CODES.get(simple_type, {
        "system": "http://snomed.info/sct",
        "code": simple_type,
        "display": simple_type
    })

def get_encounter_type_code(simple_type: str) -> dict:
    """Get encounter type code from simple type string."""
    return ENCOUNTER_TYPE_CODES.get(simple_type.lower(), {
        "system": "http://hl7.org/fhir/v3/ActCode",
        "code": simple_type.upper(),
        "display": simple_type
    })

def get_smoking_status_code(status: str) -> dict:
    """Get smoking status code from simple status string."""
    return SMOKING_STATUS_CODES.get(status.lower(), {
        "system": "http://snomed.info/sct",
        "code": status,
        "display": status
    })

def get_allergy_substance_code(substance: str) -> dict:
    """Get allergy substance code from substance name."""
    return ALLERGY_SUBSTANCE_CODES.get(substance.lower(), {
        "system": "http://snomed.info/sct",
        "code": substance,
        "display": substance
    })

def get_allergy_reaction_code(reaction: str) -> dict:
    """Get allergy reaction manifestation code from reaction name."""
    return ALLERGY_REACTION_CODES.get(reaction.lower(), {
        "system": "http://snomed.info/sct",
        "code": reaction,
        "display": reaction
    })

def get_practitioner_role_code(role: str) -> dict:
    """Get practitioner role code from simple role string."""
    return PRACTITIONER_ROLE_CODES.get(role.lower(), {
        "system": "http://snomed.info/sct",
        "code": role,
        "display": role
    })

