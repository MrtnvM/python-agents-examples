import logging
from livekit.agents.voice import Agent
from models.user_data import UserData
from agents.run_context import RunContext_T
from utils import load_prompt
import json

logger = logging.getLogger("base-agent")
logger.setLevel(logging.INFO)


class BaseAgent(Agent):
    prompt_path = ""

    async def on_enter(self) -> None:
        # Logging the current agent name
        agent_name = self.__class__.__name__
        logger.info(f"Entering {agent_name}")
        print(f"Entering {agent_name}")

        # Setting the agent name as an attribute of the local participant
        userdata: UserData = self.session.userdata
        if userdata.ctx and userdata.ctx.room:
            await userdata.ctx.room.local_participant.set_attributes(
                {"agent": agent_name}
            )

        # Truncating the chat context to keep the last n messages
        chat_ctx = self.chat_ctx.copy()

        if userdata.prev_agent:
            items_copy = self._truncate_chat_ctx(
                userdata.prev_agent.chat_ctx.items,
                keep_function_call=True,
                keep_last_n_messages=50,  # was 6 messages
            )
            existing_ids = {item.id for item in chat_ctx.items}
            items_copy = [item for item in items_copy if item.id not in existing_ids]
            chat_ctx.items.extend(items_copy)

        # Updating the chat context
        await self.update_chat_ctx(chat_ctx)

        print(chat_ctx.items)

        # Generating a reply for the agent to speak to the user
        self.session.generate_reply(allow_interruptions=False)

    def get_agent_data(self, context: RunContext_T) -> dict:
        """Get the data for the agent. Should be overridden by the child class."""
        return {}

    async def set_data(self, context: RunContext_T) -> None:
        """Set the data for the agent."""

        data = self.get_agent_data(context)
        data_str = json.dumps(data, indent=2)

        logger.info(
            f"Updating instructions for {self.prompt_path} with data: {data_str}"
        )
        await self.update_instructions(load_prompt(self.prompt_path, context=data_str))

    def _truncate_chat_ctx(
        self,
        items: list,
        keep_last_n_messages: int = 6,
        keep_system_message: bool = False,
        keep_function_call: bool = False,
    ) -> list:
        """Truncate the chat context to keep the last n messages."""

        def _valid_item(item) -> bool:
            if (
                not keep_system_message
                and item.type == "message"
                and item.role == "system"
            ):
                return False

            if not keep_function_call and item.type in [
                "function_call",
                "function_call_output",
            ]:
                return False

            return True

        new_items = []
        for item in reversed(items):
            if _valid_item(item):
                new_items.append(item)
            if len(new_items) >= keep_last_n_messages:
                break
        new_items = new_items[::-1]

        while new_items and new_items[0].type in [
            "function_call",
            "function_call_output",
        ]:
            new_items.pop(0)

        return new_items

    async def _transfer_to_agent(self, name: str, context: RunContext_T) -> Agent:
        """Transfer to another agent while preserving context"""
        userdata = context.userdata
        current_agent = context.session.current_agent
        next_agent = userdata.personas[name]

        if isinstance(next_agent, BaseAgent):
            await next_agent.set_data(context)

        userdata.prev_agent = current_agent

        return next_agent
