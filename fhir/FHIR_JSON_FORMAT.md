# FHIR JSON Format

This document describes the JSON format for representing clinical data based on the FHIR Clinical Ontology.

## Overview

The FHIR JSON format is designed to represent clinical resources in a structured JSON format that aligns with the FHIR Clinical Ontology structure. It supports all major resource types including Patient, Observation, Condition, MedicationStatement, FamilyMemberHistory, ReferralRequest, Encounter, CarePlan, AllergyIntolerance, Organization, and Practitioner.

## Structure

### Bundle Format

When representing multiple resources, use a Bundle:

```json
{
  "resourceType": "Bundle",
  "type": "collection",
  "entry": [
    {
      "resource": { /* Resource object */ }
    }
  ]
}
```

### Single Resource Format

Individual resources follow this structure:

```json
{
  "resourceType": "ResourceType",
  "id": "resource-id",
  "property1": "value1",
  "property2": { /* nested object */ }
}
```

## Resource Types

### Patient

Represents a patient in the healthcare system.

**Required Properties:**
- `resourceType`: Must be "Patient"

**Common Properties:**
- `id`: Unique identifier
- `identifier`: Array of identifier objects
- `name`: Array of name objects with `family`, `given`, `text`
- `gender`: "male" | "female" | "other" | "unknown"
- `birthDate`: Date string (YYYY-MM-DD)
- `active`: Boolean
- `nhsNumber`: NHS number string
- `capacityToConsent`: Boolean
- `interpreterRequired`: Boolean

**Example:**
```json
{
  "resourceType": "Patient",
  "id": "patienta",
  "name": [{
    "family": "PatientA",
    "given": ["Test"],
    "text": "Test PatientA"
  }],
  "gender": "female",
  "birthDate": "1956-01-15",
  "active": true,
  "nhsNumber": "1234567890",
  "capacityToConsent": true,
  "interpreterRequired": false
}
```

### Observation

Represents a clinical observation or measurement.

**Required Properties:**
- `resourceType`: Must be "Observation"
- `status`: "registered" | "preliminary" | "final" | "amended" | "corrected" | "cancelled" | "entered-in-error" | "unknown"
- `code`: CodeableConcept object

**Common Properties:**
- `id`: Unique identifier
- `subject`: Reference to Patient
- `effectiveDateTime`: ISO 8601 date-time string
- `valueQuantity`: Quantity object with `value` and `unit`
- `valueString`: String value (for non-numeric observations)
- `valueBoolean`: Boolean value
- `interpretation`: CodeableConcept
- `bodySite`: CodeableConcept
- `category`: Array of CodeableConcept objects

**Example:**
```json
{
  "resourceType": "Observation",
  "id": "obs_fit",
  "status": "final",
  "code": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "773530003",
      "display": "Faecal immunochemical test"
    }]
  },
  "subject": {
    "reference": "Patient/patienta"
  },
  "effectiveDateTime": "2024-11-08T10:00:00+00:00",
  "valueQuantity": {
    "value": 142.0,
    "unit": "µg Hb/g"
  }
}
```

### Condition

Represents a clinical condition or diagnosis.

**Required Properties:**
- `resourceType`: Must be "Condition"
- `clinicalStatus`: "active" | "recurrence" | "relapse" | "inactive" | "remission" | "resolved" | "unknown"
- `code`: CodeableConcept object

**Common Properties:**
- `id`: Unique identifier
- `subject`: Reference to Patient
- `onsetDateTime`: ISO 8601 date-time string
- `assertedDate`: ISO 8601 date-time string
- `verificationStatus`: String
- `asserter`: Reference to Practitioner
- `category`: Array of CodeableConcept objects

**Example:**
```json
{
  "resourceType": "Condition",
  "id": "cond_diabetes",
  "clinicalStatus": "active",
  "code": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "44054006",
      "display": "Diabetes mellitus type 2"
    }]
  },
  "subject": {
    "reference": "Patient/patienta"
  },
  "assertedDate": "2024-11-08T10:00:00+00:00"
}
```

### MedicationStatement

Represents a medication statement.

**Required Properties:**
- `resourceType`: Must be "MedicationStatement"
- `status`: "active" | "completed" | "entered-in-error" | "intended" | "stopped" | "on-hold" | "unknown" | "not-taken"

**Common Properties:**
- `id`: Unique identifier
- `medicationReference`: Reference to Medication
- `medicationCodeableConcept`: CodeableConcept (alternative to medicationReference)
- `subject`: Reference to Patient
- `taken`: "y" | "n" | "unk" | "na"
- `dateAsserted`: ISO 8601 date-time string
- `effectiveDateTime`: ISO 8601 date-time string
- `dosage`: Array of Dosage objects
- `note`: Array of Annotation objects

**Example:**
```json
{
  "resourceType": "MedicationStatement",
  "id": "med_metformin",
  "status": "active",
  "medicationReference": {
    "reference": "Medication/metformin"
  },
  "subject": {
    "reference": "Patient/patienta"
  },
  "taken": "y",
  "dateAsserted": "2024-11-08T10:00:00+00:00",
  "effectiveDateTime": "2024-01-01T00:00:00+00:00"
}
```

### FamilyMemberHistory

Represents family member history information.

**Required Properties:**
- `resourceType`: Must be "FamilyMemberHistory"
- `status`: "partial" | "completed" | "entered-in-error" | "health-unknown"
- `patient`: Reference to Patient

**Common Properties:**
- `id`: Unique identifier
- `relationship`: CodeableConcept
- `gender`: "male" | "female" | "other" | "unknown"
- `condition`: Array of condition objects with `code` and `outcome`
- `notDoneReason`: CodeableConcept

**Example:**
```json
{
  "resourceType": "FamilyMemberHistory",
  "id": "fmh_brother_crc",
  "status": "completed",
  "patient": {
    "reference": "Patient/patienta"
  },
  "relationship": {
    "coding": [{
      "system": "http://hl7.org/fhir/v3/RoleCode",
      "code": "BRO",
      "display": "brother"
    }]
  },
  "gender": "male",
  "condition": [{
    "code": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "363418001",
        "display": "Malignant neoplasm of colon"
      }]
    },
    "outcome": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "419099009",
        "display": "Dead"
      }]
    }
  }]
}
```

### ReferralRequest

Represents a referral request.

**Required Properties:**
- `resourceType`: Must be "ReferralRequest"
- `status`: "draft" | "active" | "suspended" | "cancelled" | "completed" | "entered-in-error" | "unknown"
- `intent`: "proposal" | "plan" | "order" | "original-order" | "reflex-order" | "filler-order" | "instance-order" | "option"
- `subject`: Reference to Patient

**Common Properties:**
- `id`: Unique identifier
- `type`: CodeableConcept
- `context`: Reference to Encounter
- `authoredOn`: ISO 8601 date-time string
- `requester`: Object with `agent` and `onBehalfOf` references
- `recipient`: Array of Organization references
- `reasonCode`: Array of CodeableConcept objects
- `serviceRequested`: Array of CodeableConcept objects
- `specialty`: CodeableConcept

**Example:**
```json
{
  "resourceType": "ReferralRequest",
  "id": "ref_colorectal",
  "status": "active",
  "intent": "order",
  "type": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "713400007",
      "display": "Referral to colorectal surgery"
    }]
  },
  "subject": {
    "reference": "Patient/patienta"
  },
  "authoredOn": "2024-11-08T12:00:00+00:00",
  "reasonCode": [{
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "422768004",
      "display": "Urgent two-week-wait colorectal pathway referral"
    }]
  }]
}
```

## Common Data Types

### CodeableConcept

Represents a coded concept with optional text.

```json
{
  "coding": [
    {
      "system": "http://snomed.info/sct",
      "code": "44054006",
      "display": "Diabetes mellitus type 2"
    }
  ],
  "text": "Type 2 diabetes"
}
```

### Coding

Represents a single code from a coding system.

```json
{
  "system": "http://snomed.info/sct",
  "code": "44054006",
  "display": "Diabetes mellitus type 2"
}
```

### Reference

Represents a reference to another resource.

```json
{
  "reference": "Patient/patienta",
  "display": "Patient A"
}
```

### Quantity

Represents a quantity with value and unit.

```json
{
  "value": 142.0,
  "unit": "µg Hb/g",
  "system": "http://unitsofmeasure.org",
  "code": "ug/g"
}
```

### Address

Represents an address.

```json
{
  "line": ["123 Main Street"],
  "city": "London",
  "district": "Westminster",
  "postalCode": "SW1A 1AA",
  "type": "both",
  "text": "123 Main Street, London, SW1A 1AA"
}
```

### ContactPoint

Represents contact information.

```json
{
  "system": "phone",
  "value": "+44 20 1234 5678"
}
```

### Period

Represents a time period.

```json
{
  "start": "2024-01-01T00:00:00+00:00",
  "end": "2024-12-31T23:59:59+00:00"
}
```

## Coding Systems

Common coding systems used:

- **SNOMED CT**: `http://snomed.info/sct`
- **LOINC**: `http://loinc.org`
- **ICD-10**: `http://hl7.org/fhir/sid/icd-10`
- **NHS Data Dictionary**: `https://fhir.nhs.uk/STU3/CodeSystem/...`

## Date/Time Formats

- **Date**: `YYYY-MM-DD` (e.g., "1956-01-15")
- **DateTime**: ISO 8601 format with timezone (e.g., "2024-11-08T10:00:00+00:00")

## Files

- `fhir_json_schema.json`: JSON Schema definition for validation
- `patienta.json`: Example JSON file based on patienta.ttl

## Validation

You can validate JSON files against the schema using any JSON Schema validator:

```bash
# Using ajv-cli (npm install -g ajv-cli)
ajv validate -s fhir_json_schema.json -d patienta.json
```

## Mapping from TTL

The JSON format directly maps to the TTL ontology structure:

- TTL individuals → JSON resources with `id`
- TTL object properties → JSON references
- TTL data properties → JSON primitive values
- TTL CodeableConcept/Coding → JSON nested objects
- TTL Quantity → JSON Quantity objects

