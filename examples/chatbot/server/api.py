from langchain.chains import LLMChain
from prompt import CHATBOT_PROMPT
from steamship.invocable import PackageService, get, post

from steamship_langchain.llms import SteamshipGPT
from steamship_langchain.memory import (
    SteamshipPersistentConversationMemory,
    SteamshipPersistentConversationWindowMemory,
)


class ChatbotPackage(PackageService):
    @post("/send_message")
    def send_message(self, message: str, chat_history_handle: str) -> str:
        """Returns an AI-generated response to a user conversation, based on limited prior context."""

        # steamship_memory will persist/retrieve conversation across API calls
        steamship_memory = SteamshipPersistentConversationWindowMemory(
            client=self.client, file_handle=chat_history_handle, k=2
        )
        chatgpt = LLMChain(
            llm=SteamshipGPT(client=self.client, temperature=0),
            prompt=CHATBOT_PROMPT,
            memory=steamship_memory,
        )
        return chatgpt.predict(human_input=message)

    @get("/transcript")
    def transcript(self, chat_history_handle: str) -> str:
        """Return the full transcript for a chat session."""
        steamship_memory = SteamshipPersistentConversationMemory(
            client=self.client, file_handle=chat_history_handle
        )

        return steamship_memory.load_memory_variables(inputs={}).get("history", "")
