import logging
from typing import override

from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent
from livekit.plugins import cartesia, deepgram, openai, silero

from agents.base_agent import BaseAgent
from agents.run_context import RunContext_T
from utils import load_prompt

logger = logging.getLogger("confirmation-agent")
logger.setLevel(logging.INFO)


class ConfirmationAgent(BaseAgent):
    prompt_path = "agents/confirmation.yaml"

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

    @override
    def get_agent_data(self, context: RunContext_T) -> dict:
        """Get the data for the confirmation agent."""
        return {
            "patient": context.userdata.patient,
            "symptom_form": context.userdata.symptom_form,
            "med_info_form": context.userdata.med_info_form,
        }

    @function_tool()
    async def confirm(self, context: RunContext_T) -> Agent:
        """
        CALL THIS FUNCTION WHEN THE PATIENT CONFIRMS THE INFORMATION PROVIDED.
        """

        logger.info("Patient confirmed the information provided.")

        await self.session.say(
            "Thank you for providing the information. You medical provider will review the information and get back to you shortly. Have a great day!"
        )

        return None
