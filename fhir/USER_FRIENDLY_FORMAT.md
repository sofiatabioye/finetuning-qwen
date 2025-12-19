# User-Friendly JSON Format

## Overview

This document describes a simplified, user-friendly JSON format designed for easy reading and writing by application users. This format is then mapped to the full FHIR ontology format using a mapper.

## Design Principles

1. **Simplicity**: Flat structure, minimal nesting
2. **Readability**: Clear field names, no complex references
3. **Completeness**: Contains all necessary clinical information
4. **Mappable**: Can be automatically converted to full FHIR ontology

## Format Structure

### Patient

Simple patient object with all demographics:

```json
{
  "patient": {
    "id": "patienta",
    "name": {
      "family": "PatientA",
      "given": ["Test"],
      "text": "Test PatientA"
    },
    "gender": "female",
    "birthDate": "1956-01-15",
    "nhsNumber": "1234567890",
    "capacityToConsent": true,
    "interpreterRequired": false,
    "address": {
      "line": ["123 Main Street"],
      "city": "London",
      "postalCode": "SW1A 1AA"
    },
    "contact": {
      "phone": "+44 20 1234 5678",
      "email": "patient@example.com"
    }
  }
}
```

### Observations

Array of simple observation objects:

```json
{
  "observations": [
    {
      "id": "obs_fit",
      "code": "fit",
      "display": "Faecal immunochemical test",
      "value": 142.0,
      "unit": "µg Hb/g",
      "date": "2024-11-08T10:00:00+00:00",
      "status": "final"
    }
  ]
}
```

**Key Features:**
- Simple `code` string (e.g., "fit", "hb", "ferritin")
- Direct `value` and `unit` properties
- No complex CodeableConcept nesting
- Mapper handles SNOMED/LOINC code lookup

### Conditions

Array of condition objects:

```json
{
  "conditions": [
    {
      "id": "cond_diabetes",
      "code": "diabetesType2",
      "display": "Diabetes mellitus type 2",
      "status": "active",
      "onsetDate": "2024-08-01",
      "assertedDate": "2024-11-08"
    }
  ]
}
```

**Key Features:**
- Simple `code` string (e.g., "diabetesType2", "hypertension")
- Status: "active" | "resolved" | "inactive"
- Simple date strings (YYYY-MM-DD)
- Mapper handles SNOMED code mapping

### Medications

Array of medication objects:

```json
{
  "medications": [
    {
      "id": "med_metformin",
      "name": "Metformin",
      "status": "active",
      "taken": "y",
      "startDate": "2024-01-01",
      "assertedDate": "2024-11-08"
    }
  ]
}
```

**Key Features:**
- Simple `name` string
- Status: "active" | "stopped" | "completed"
- Taken: "y" | "n" | "unk" | "na"
- Mapper handles medication code lookup

### Family History

Array of family history objects:

```json
{
  "familyHistory": [
    {
      "id": "fmh_brother_crc",
      "relationship": "brother",
      "gender": "male",
      "condition": {
        "code": "colorectalCancer",
        "display": "Malignant neoplasm of colon",
        "ageAtDiagnosis": 62
      },
      "status": "completed"
    }
  ]
}
```

**Key Features:**
- Simple relationship string: "brother" | "mother" | "father" | "sister" | etc.
- Nested condition object with code and display
- Mapper handles relationship and condition code mapping

### Referral

Single referral object:

```json
{
  "referral": {
    "id": "ref_colorectal",
    "type": "colorectalSurgery",
    "display": "Referral to colorectal surgery",
    "status": "active",
    "intent": "order",
    "priority": "urgent",
    "reason": "Urgent two-week-wait colorectal pathway referral",
    "authoredDate": "2024-11-08T12:00:00+00:00"
  }
}
```

### Encounter

Single encounter object:

```json
{
  "encounter": {
    "id": "enc1",
    "status": "in-progress",
    "type": "outpatient",
    "date": "2024-11-08T10:00:00+00:00",
    "reason": "Urgent two-week-wait colorectal referral"
  }
}
```

### Organization

Single organization object:

```json
{
  "organization": {
    "id": "org1",
    "name": "NHS Trust Hospital",
    "odsCode": "ABC123"
  }
}
```

### Allergies

Array of allergy objects:

```json
{
  "allergies": [
    {
      "id": "alg1",
      "substance": "Penicillin",
      "display": "Penicillin allergy",
      "type": "allergy",
      "category": "medication",
      "clinicalStatus": "active",
      "verificationStatus": "confirmed",
      "criticality": "high",
      "reaction": {
        "manifestation": "Anaphylaxis",
        "onsetDate": "2010-05-15"
      },
      "assertedDate": "2010-05-15"
    }
  ]
}
```

**Key Features:**
- Simple `substance` string (e.g., "Penicillin", "Aspirin", "Peanuts")
- `type`: "allergy" | "intolerance"
- `category`: "medication" | "food" | "environment" | "biologic"
- `criticality`: "low" | "high" | "unable-to-assess"
- `reaction`: Object with `manifestation` and `onsetDate`
- Mapper handles SNOMED code lookup for substances and reactions

### Social History

Object containing smoking and alcohol information:

```json
{
  "socialHistory": {
    "smokingStatus": {
      "status": "former",
      "packYears": 20,
      "quitDate": "2012-01-01",
      "quitYearsAgo": 12
    },
    "alcohol": {
      "unitsPerWeek": 7,
      "pattern": "6-8 units per week",
      "status": "current"
    }
  }
}
```

**Key Features:**
- **Smoking Status:**
  - `status`: "never" | "current" | "former"
  - `packYears`: Number (for former/current smokers)
  - `quitDate`: Date string (for former smokers)
  - `quitYearsAgo`: Number (calculated or provided)
  
- **Alcohol:**
  - `unitsPerWeek`: Number
  - `pattern`: Descriptive string
  - `status`: "current" | "former" | "never"
  
- Mapper handles SNOMED code mapping for smoking status

## Code Mapping

The mapper uses a code mapping table to convert simple codes to full SNOMED/LOINC codes:

### Observation Codes

```python
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
    "ferritin": {
        "system": "http://loinc.org",
        "code": "2276-4",
        "display": "Ferritin"
    },
    # ... more codes
}
```

### Condition Codes

```python
CONDITION_CODES = {
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
    # ... more codes
}
```

### Relationship Codes

```python
RELATIONSHIP_CODES = {
    "brother": {
        "system": "http://hl7.org/fhir/v3/RoleCode",
        "code": "BRO",
        "display": "brother"
    },
    "mother": {
        "system": "http://hl7.org/fhir/v3/RoleCode",
        "code": "MTH",
        "display": "mother"
    },
    # ... more codes
}
```

## Mapping Process

The mapper (`mapper.py`) performs the following transformations:

1. **Code Expansion**: Converts simple codes to full CodeableConcept objects
2. **Reference Creation**: Creates proper resource references
3. **Date Normalization**: Converts dates to proper ISO 8601 format
4. **Resource Linking**: Links all resources to the patient
5. **Ontology Generation**: Creates RDF triples in TTL format

## Benefits

### For Users
- ✅ Easy to read and understand
- ✅ Simple to fill in forms
- ✅ No need to know SNOMED codes
- ✅ Minimal nesting and complexity

### For Developers
- ✅ Clear structure for UI forms
- ✅ Easy validation
- ✅ Straightforward API design
- ✅ Automatic conversion to full FHIR

### For System
- ✅ Consistent data structure
- ✅ Automatic code mapping
- ✅ Full FHIR compliance via mapper
- ✅ Maintainable code base

## Example: User-Friendly → FHIR Ontology

**Input (User-Friendly):**
```json
{
  "observations": [{
    "code": "fit",
    "value": 142.0,
    "unit": "µg Hb/g"
  }]
}
```

**Output (FHIR Ontology TTL):**
```turtle
:obs_fit rdf:type owl:NamedIndividual , :Observation ;
    :Observation_code :obs_fit_code ;
    :Observation_valueQuantity :obs_fit_qty ;
    :Observation_subject :patienta .

:obs_fit_code rdf:type owl:NamedIndividual , :CodeableConcept ;
    :CodeableConcept_coding :obs_fit_coding .

:obs_fit_coding rdf:type owl:NamedIndividual , :Coding ;
    :Coding_system "http://snomed.info/sct"^^xsd:anyURI ;
    :Coding_code "773530003" ;
    :Coding_display "Faecal immunochemical test" .

:obs_fit_qty rdf:type owl:NamedIndividual , :Quantity ;
    :Quantity_value 142.0 ;
    :Quantity_unit "µg Hb/g" .
```

## Comparison

| Aspect | User-Friendly Format | Full FHIR Format |
|--------|---------------------|------------------|
| **Readability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Verbosity** | Low | High |
| **Code Knowledge** | Not required | Required |
| **Nesting** | Minimal | Deep |
| **References** | Implicit | Explicit |
| **FHIR Compliance** | Via mapper | Direct |

## Next Steps

1. ✅ Define user-friendly format structure
2. ✅ Create code mapping tables
3. ✅ Extend mapper.py to handle new format
4. ✅ Create validation schema
5. ✅ Build UI forms based on format
6. ✅ Test end-to-end conversion

