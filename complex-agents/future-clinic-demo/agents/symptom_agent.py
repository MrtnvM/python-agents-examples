import logging

from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent
from livekit.plugins import cartesia, deepgram, openai, silero

from agents.base_agent import BaseAgent
from agents.run_context import RunContext_T
from utils import load_prompt
from models.symptom_form import SymptomForm

logger = logging.getLogger("symptom-agent")
logger.setLevel(logging.INFO)


class SymptomAgent(BaseAgent):
    prompt_path = "agents/symptom.yaml"

    def __init__(self, lang: str = "en-US") -> None:
        super().__init__(
            instructions=load_prompt(self.prompt_path),
            stt=deepgram.STT(model="nova-3-medical", language=lang),
            llm=openai.LLM(model="gpt-4.1-2025-04-14"),
            tts=cartesia.TTS(
                model="sonic-2",
                speed="fast",
                language=lang,
                # voice="5c42302c-194b-4d0c-ba1a-8cb485c84ab9",
                emotion=["positivity:lowest"],
            ),
            vad=silero.VAD.load(),
        )

    @function_tool()
    async def update_symptom_form(
        self, context: RunContext_T, form: SymptomForm
    ) -> Agent:
        """
        Update the symptom form with the given form schema
        if the patient has provided ANY of the information.

        CALL THIS FUNCTION EVERY TIME THE PATIENT PROVIDES ANY OF THE INFORMATION.
        """

        logger.info(f"Updating symptom form: {form}")
        context.userdata.symptom_form = form
        return None

    @function_tool()
    async def finish_symptom_collection(self, context: RunContext_T) -> Agent:
        """
        If the patient has provided ENOUGH DETAIL to provide a complete picture for a doctor,
        finish the symptom collection and transfer to the med info agent.

        CALL THIS FUNCTION WHEN THE PATIENT HAS PROVIDED ENOUGH DETAIL TO PROVIDE A COMPLETE PICTURE FOR A DOCTOR.
        """

        await self.session.say(
            "Thank you for providing the information. Let's talk about your medical history."
        )

        return await self._transfer_to_agent("med_info", context)
