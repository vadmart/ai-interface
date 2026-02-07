import logging
import uuid
from typing import AsyncIterator

from starlette.testclient import TestClient

from ai_client import ollama_client, MODEL_NAME
from ollama import Message, ChatResponse
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket, WebSocketDisconnect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ws_debug")
app = FastAPI()

template = Jinja2Templates(directory="templates")

MODEL_MESSAGES: list[Message] = [Message(role="system", content="You're a computer science nerd who answers with a bit of sarcasm")]

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
            stream: AsyncIterator[ChatResponse] = await ollama_client.chat(MODEL_NAME, data=data, messages=MODEL_MESSAGES, stream=True)
            message_id = uuid.uuid4().hex
            async for part in stream:
                await websocket.send({"id": message_id, **part.message})
            logger.info(f"WebSocket message: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as ex:
        logger.error(ex)
        try:
            await websocket.close(code=1011)
        except:
            pass


def test_websocket(websocket: WebSocket):
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:

        data = websocket.receive_json()
        assert data
