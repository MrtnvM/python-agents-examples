from dataclasses import dataclass, field
from typing import List


@dataclass
class SymptomInput:
    """A model for a symptom input."""

    name: str = field(default="", metadata={"description": "The name of the symptom"})
    sites: List[str] = field(
        default_factory=list,
        metadata={"description": "The sites of the symptom (e.g. head, chest, etc.)"},
    )
    onset: str = field(
        default="",
        metadata={
            "description": "The onset of the symptom (e.g. sudden, gradual, etc.)"
        },
    )
    timing: str = field(
        default="",
        metadata={
            "description": "The timing of the symptom (e.g. daily, intermittent, etc.)"
        },
    )
    triggers: List[str] = field(
        default_factory=list,
        metadata={
            "description": "The triggers of the symptom (e.g. stress, exercise, etc.)"
        },
    )
    alleviating_factors: List[str] = field(
        default_factory=list,
        metadata={
            "description": "The alleviating factors of the symptom (e.g. rest, medication, etc.)"
        },
    )
    worsening_factors: List[str] = field(
        default_factory=list,
        metadata={
            "description": "The worsening factors of the symptom (e.g. stress, exercise, etc.)"
        },
    )


@dataclass
class SymptomForm:
    """A model for a patient symptom form."""

    chief_complaint: str = field(
        default="",
        metadata={"description": "The chief complaint of the patient"},
    )
    symptoms: List[SymptomInput] = field(
        default_factory=list,
        metadata={
            "description": "The symptoms of the patient (e.g. headache, fever, etc.)"
        },
    )
