import logging

from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession, room_io
from livekit.plugins import noise_cancellation

from agents.symptom_agent import SymptomAgent
from agents.med_info_agent import MedInfoAgent
from agents.confirmation_agent import ConfirmationAgent
from models.patient import Patient
from models.user_data import UserData

logger = logging.getLogger("demo-agent")
logger.setLevel(logging.INFO)

load_dotenv()


# Entrypoint for the whole agent system
async def entrypoint(ctx: JobContext):
    # Connect to the LiveKit server
    await ctx.connect()

    # Crete mock data
    patient = Patient(
        name="John Doe",
        age=30,
        gender="male",
        city="New York",
        state="NY",
        country="USA",
    )

    # Create the userdata object
    userdata = UserData(ctx=ctx, patient=patient)

    # Create agents
    symptom_agent = SymptomAgent()
    med_info_agent = MedInfoAgent()
    confirmation_agent = ConfirmationAgent()

    logger.info("Setting data for symptom agent")
    print("Printing: Setting data for symptom agent")
    await symptom_agent.set_data(userdata)

    # Register all agents in the userdata
    userdata.personas.update(
        {
            "symptom": symptom_agent,
            "med_info": med_info_agent,
            "confirmation": confirmation_agent,
        }
    )

    # Create the session
    session = AgentSession[UserData](userdata=userdata)

    # Start the session
    await session.start(
        agent=symptom_agent,
        room=ctx.room,
        room_input_options=room_io.RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
