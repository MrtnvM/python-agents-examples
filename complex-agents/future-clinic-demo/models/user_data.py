from dataclasses import dataclass, field
from typing import Optional

from livekit.agents import JobContext
from livekit.agents.voice import Agent

from models.patient import Patient
from models.med_info_form import MedInfoForm
from models.symptom_form import SymptomForm


@dataclass
class UserData:
    """Stores data and agents to be shared across the session"""

    personas: dict[str, Agent] = field(
        default_factory=dict,
        metadata={"description": "A dictionary of agents that can be transferred to"},
    )
    prev_agent: Optional[Agent] = field(
        default=None,
        metadata={"description": "The previous agent that the user was transferred to"},
    )
    ctx: Optional[JobContext] = field(
        default=None,
        metadata={"description": "The job context"},
    )

    patient: Patient = field(
        default_factory=Patient,
        metadata={"description": "The patient's information"},
    )
    symptom_form: SymptomForm = field(
        default_factory=SymptomForm,
        metadata={"description": "The patient's symptom form"},
    )
    med_info_form: MedInfoForm = field(
        default_factory=MedInfoForm,
        metadata={"description": "The patient's medical information"},
    )

    def summarize(self) -> str:
        return "User data: Medical office triage system"
