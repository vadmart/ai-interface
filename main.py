import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator, Coroutine, Any

from pydantic import BaseModel
from starlette.testclient import TestClient

from ollama import ChatResponse
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket, WebSocketDisconnect

from config import OLLAMA_HOST
from services.llm_client import llm_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ws_debug")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await llm_client.connect(host=OLLAMA_HOST)
    yield
    await llm_client.disconnect()


app = FastAPI(lifespan=lifespan)

template = Jinja2Templates(directory="templates")


# -------------------------------------------------------------------
# Schemas and Routes (Temporarily here)
# -------------------------------------------------------------------
class ChatRequest(BaseModel):
    model_name: str
    prompt: dict

@app.get("/")
def read_root(request: Request):
    return template.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        logger.info("WebSocket connection accepted")
        while True:
            data = await websocket.receive_json()
            stream = llm_client.chat(model_name="gpt-oss-120b:cpu", messages=data)
            message_id = uuid.uuid4().hex
            async for part in await stream:
                await websocket.send_json(
                    {"id": message_id, "content": part.message.content, "role": part.message.role})
            logger.info(f"WebSocket message: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as ex:
        logger.exception(ex)
        try:
            await websocket.close(code=1011)
        except:
            pass


def test_websocket():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        message = {"id": uuid.uuid4().hex, "content": "Hello World", "role": "user"}
        websocket.send_json(message)
        for _ in range(3):
            data = websocket.receive_json()
            assert {"id", "content", "role"} <= data.keys()


if __name__ == "__main__":
    test_websocket()
