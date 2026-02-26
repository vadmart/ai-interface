import asyncio
from typing import Optional, Coroutine, Any, AsyncIterator

import ollama
from ollama import AsyncClient, ChatResponse, Message


# -------------------------------------------------------------------
# Global LLM Client handling connection to AI models
# -------------------------------------------------------------------
class GlobalLLMClient:
    def __init__(self):
        self.is_connected = False
        self.session: Optional[AsyncClient] = None

    async def connect(self, host: str):
        """Initialize the connection pool or async session."""
        self.is_connected = True
        self.session = ollama.AsyncClient(host=host)
        print("Global LLM Client connected.")

    async def disconnect(self):
        """Clean up resources on app shutdown."""
        self.is_connected = False
        self.session = None
        print("Global LLM Client disconnected.")

    async def chat(self, model_name: str, messages: list[Message]) -> AsyncIterator[ChatResponse]:
        """Fetch response from the specific model."""
        if not self.is_connected:
            raise RuntimeError("LLM Client is not connected.")
        return await self.session.chat(model=model_name, messages=messages, stream=True)

        # Simulate processing time for the model
        await asyncio.sleep(1)
        return f"[Model: {model_name}] Response for '{prompt}'"


# Instantiate the client here so it acts as a Singleton across the app
llm_client = GlobalLLMClient()