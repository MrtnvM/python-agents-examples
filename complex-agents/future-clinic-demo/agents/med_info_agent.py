import logging

from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent
from livekit.plugins import cartesia, deepgram, openai, silero

from agents.base_agent import BaseAgent
from agents.run_context import RunContext_T
from utils import load_prompt
from models.med_info_form import MedInfoForm

logger = logging.getLogger("med-info-agent")
logger.setLevel(logging.INFO)


class MedInfoAgent(BaseAgent):
    prompt_path = "agents/med_info.yaml"

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

    def get_agent_data(self, context: RunContext_T) -> dict:
        """Get the data for the med info agent."""
        return {
            "patient": context.userdata.patient,
            "symptom_form": context.userdata.symptom_form,
        }

    @function_tool()
    async def update_med_info_form(
        self, context: RunContext_T, form: MedInfoForm
    ) -> Agent:
        """
        Update the med info form with the given form schema
        if the patient has provided ANY of the information.

        CALL THIS FUNCTION EVERY TIME THE PATIENT PROVIDES ANY OF THE INFORMATION.
        """

        logger.info(f"Updating med info form: {form}")
        context.userdata.med_info_form = form
        return None

    @function_tool()
    async def finish_med_info_collection(self, context: RunContext_T) -> Agent:
        """Finish the med info collection and transfer to the confirmation agent."""

        await self.session.say(
            "Thank you for providing the information. Let's go to the final step."
        )

        return await self._transfer_to_agent("confirmation", context)
