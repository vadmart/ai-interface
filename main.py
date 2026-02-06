import logging

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
            data = await websocket.receive()
            logger.info(f"WebSocket message: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as ex:
        logger.error(ex)
        try:
            await websocket.close(code=1011)
        except:
            pass
