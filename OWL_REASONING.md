# OWL Reasoning for Colorectal Referral Ontology

This document explains how the reasoning rules are implemented in the OWL ontology for standardization.

## Overview

The reasoning rules have been implemented in the ontology using:
1. **OWL Class Definitions**: Value range classes and patient classification classes
2. **SWRL Rules**: Semantic Web Rule Language rules for complex logical conditions

## Files

- `colorectal_ontology.ttl`: Main ontology with class definitions and SWRL rule descriptions
- `colorectal_rules.swrl`: SWRL rules file for use with SWRL-enabled reasoners

## OWL Class Structure

### Observation Value Range Classes

These classes classify observations based on numeric values:

- `HighFIT_Result`: FIT results with value > 100 µg Hb/g
- `PositiveFIT_Result`: FIT results with value > 10 µg Hb/g
- `LowHaemoglobin_Result`: Haemoglobin results with value < 120 g/L
- `LowFerritin_Result`: Ferritin results with value < 30 µg/L

**Note**: The actual numeric classification is done via SWRL rules since OWL 2 DL has limited support for datatype restrictions with comparisons.

### Patient Classification Classes

These classes represent patients matching specific clinical criteria:

- `PatientWithHighFITAndSymptoms`: Patient with FIT > 100 AND (ChangeInBowelHabit OR RectalBleeding OR UnintentionalWeightLoss)
- `PatientWithIDAAndFamilyHistory`: Patient with IronDeficiencyAnaemia AND FamilyHistoryOfColorectalCancer
- `PatientWithLowHBAndFerritin`: Patient with Haemoglobin < 120 AND Ferritin < 30
- `PatientWithPositiveFIT`: Patient with FIT > 10

### Guidance Classes

These classes represent guidance that should be provided:

- `UrgentReferralGuidance`: Guidance for urgent referral
- `LynchScreeningGuidance`: Guidance for Lynch syndrome screening
- `IronTreatmentGuidance`: Guidance for iron treatment
- `ColonoscopyGuidance`: Guidance for colonoscopy

## SWRL Rules

The SWRL rules file (`colorectal_rules.swrl`) contains 12 rules:

### Classification Rules (Rules 1-4)
Classify observations into value range classes based on numeric values.

### Patient Classification Rules (Rules 5-8)
Classify patients into clinical criteria classes based on their observations and conditions.

### Guidance Generation Rules (Rules 9-12)
Generate guidance and actions for classified patients.

## Using OWL Reasoning

### Option 1: Using Protégé (Recommended)

1. **Install Protégé**: Download from https://protege.stanford.edu/
2. **Load Ontology**: Open `colorectal_ontology.ttl` in Protégé
3. **Load SWRL Rules**: 
   - Go to "SWRL Rules" tab
   - Import rules from `colorectal_rules.swrl` or enter manually
4. **Run Reasoner**:
   - Select a reasoner (Pellet, HermiT, or FaCT++)
   - Click "Start reasoner"
   - The reasoner will infer new class memberships
5. **Query Results**:
   - Use SPARQL queries to find patients in classification classes
   - Query for guidance instances

### Option 2: Using Python with OWL Reasoner

```python
from owlready2 import *
from rdflib import Graph

# Load ontology
onto = get_ontology("colorectal_ontology.ttl").load()

# Load patient data
patient_graph = Graph()
patient_graph.parse("onto.ttl", format="turtle")

# Merge with ontology
# (Implementation depends on reasoner library)

# Run reasoner
# (Use Pellet, HermiT, or other OWL reasoner via Python bindings)
```

### Option 3: Using Java with Pellet/HermiT

```java
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.*;

// Load ontology
OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
OWLOntology ontology = manager.loadOntologyFromOntologyDocument(
    new File("colorectal_ontology.ttl"));

// Create reasoner
OWLReasoner reasoner = new PelletReasonerFactory().createReasoner(ontology);

// Classify
reasoner.precomputeInferences();

// Query for patient classifications
// ...
```

## Benefits of OWL Reasoning

1. **Standardization**: Rules are defined in standard OWL/SWRL format
2. **Interoperability**: Can be used with any OWL-compliant reasoner
3. **Verification**: Rules can be validated independently
4. **Maintainability**: Rules are declarative and easier to update
5. **Integration**: Can integrate with other OWL-based healthcare systems

## Limitations

1. **Numeric Comparisons**: OWL 2 DL has limited support for datatype restrictions with comparisons. SWRL is needed for numeric comparisons.
2. **Complex Logic**: Some complex logical operations are easier in SWRL than pure OWL.
3. **Reasoner Dependency**: Requires a SWRL-enabled reasoner (Pellet, HermiT, or Protégé).

## Comparison with Python Rules

| Aspect | OWL/SWRL Rules | Python Rules |
|--------|----------------|--------------|
| Standardization | ✅ Standard format | ❌ Custom format |
| Interoperability | ✅ Any OWL reasoner | ❌ Python-specific |
| Numeric comparisons | ⚠️ Requires SWRL | ✅ Native support |
| Complex logic | ⚠️ Limited | ✅ Full support |
| Performance | ⚠️ Can be slower | ✅ Fast |
| Ease of use | ⚠️ Requires reasoner | ✅ Direct execution |

## Recommendation

For **standardization and interoperability**, use OWL/SWRL rules.
For **performance and ease of development**, use Python rules.

Both approaches can coexist - the ontology provides the standard definition, while Python provides the practical implementation.

