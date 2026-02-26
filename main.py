import logging
import uuid
from typing import AsyncIterator, Coroutine, Any

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
            stream: Coroutine[Any, Any, AsyncIterator[ChatResponse]] = ollama_client.chat(MODEL_NAME, messages=data, stream=True)
            message_id = uuid.uuid4().hex
            async for part in await stream:
                await websocket.send_json({"id": message_id, "content": part.message.content, "role": part.message.role})
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
