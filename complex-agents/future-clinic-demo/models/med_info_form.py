from dataclasses import dataclass, field
from typing import List


@dataclass
class AllergyInput:
    """A model for an allergy input.

    Represents a patient's allergy with cause, symptom, and severity information.
    """

    cause: str = ""
    symptom: str = ""
    severity: str = ""


@dataclass
class MedInfoForm:
    """A model for a patient medical information form.

    Contains comprehensive fields for collecting a patient's medical background,
    including medical history, family history, medications, and allergies.
    """

    past_medical_history: List[str] = field(default_factory=list)
    family_history: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    otc_medications: List[str] = field(default_factory=list)
    allergies: List[AllergyInput] = field(default_factory=list)
