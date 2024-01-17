import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, Agent
from typing import Optional, List, Dict, Any, Union, Callable, Literal, Tuple
from dotenv import load_dotenv
from functions import search_google_maps, SEARCH_GOOGLE_MAPS_SCHEMA

load_dotenv()

config_list = [{
    'model': 'gpt-3.5-turbo-1106',
    'api_key': os.getenv("OPENAI_API_KEY"),
}]


class AgentGroup:

    def __init__(self):
        self.user_proxy = UserProxyAgent(
            "user_proxy",
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
            human_input_mode="NEVER",
            code_execution_config=False
        )
        self.user_proxy.register_reply([Agent, None], AgentGroup.terminate_agent_at_reply)

        self.location_researcher = AssistantAgent(
            "location_researcher",
            human_input_mode="NEVER",
            system_message="You are the location researcher who is helping the Tour Agent plan a trip according to user requirements. You can use the `search_google_maps` function to retrieve details about a certain location, attractions, restaurants, accommodation, etc. for your research. You process results from these functions and present your findings to the Tour Agent to help them with itinerary and trip planning.",
            llm_config={
                "config_list": config_list,
                "cache_seed": None,
                "functions": [
                    SEARCH_GOOGLE_MAPS_SCHEMA,
                ]
            },
            function_map={
                "search_google_maps": search_google_maps
            }
        )

        self.tour_agent = AssistantAgent(
            "tour_agent",
            human_input_mode="NEVER",
            llm_config={
                "config_list": config_list,
                "cache_seed": None
            },
            system_message="You are a Tour Agent who helps users plan a trip based on user requirements. You can get help from the Location Researcher to research and find details about a certain location, attractions, restaurants, accommodation, etc. You use those details a answer user questions, create trip itineraries, make recommendations with practical logistics according to the user's requirements. Report the final answer when you have finalized it. Add TERMINATE to the end of this report."
        )

        self.group_chat = GroupChat(
            agents=[self.user_proxy, self.location_researcher, self.tour_agent],
            messages=[],
            allow_repeat_speaker=False,
            max_round=20
        )

        self.group_chat_manager = GroupChatManager(
            self.group_chat,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
            llm_config={
                "config_list": config_list,
                "cache_seed": None
            }
        )

    def process_user_message(self, message: str) -> str:
        self.user_proxy.initiate_chat(self.group_chat_manager, message=message, clear_history=False)
        return self._find_last_non_empty_message()

    def _find_last_non_empty_message(self) -> str:
        conversation = self.tour_agent.chat_messages[self.group_chat_manager]
        for i in range(len(conversation) - 1, -1, -1):
            if conversation[i].get("role") == "assistant":
                reply = conversation[i].get("content", "").strip()
                reply = reply.replace("TERMINATE", "")
                if reply:
                    return reply
        return "No reply received"

    @staticmethod
    def terminate_agent_at_reply(
            recipient: Agent,
            messages: Optional[List[Dict]] = None,
            sender: Optional[Agent] = None,
            config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, None]]:
        return True, None
