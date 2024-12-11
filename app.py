import asyncio
import logging
from threading import Thread

import uvicorn
from chzzk import Chzzk, ChzzkChat
from chzzk.model import ChatMessage
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocketDisconnect, WebSocket
from jinja2 import Environment, FileSystemLoader

import tts
from config import load_config, get_env
from manager import ConnectionManager

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(message)s",
)

_log = logging.getLogger(__name__)

load_config()  # 환경변수 등록
app = FastAPI()
manager = ConnectionManager()
chzzk = Chzzk() if get_env("is_login") == "false" else Chzzk.from_data(auth=get_env("nid_aut"), session=get_env("nid_ses"))
chzzk_chat = ChzzkChat(chzzk=chzzk)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Environment(loader=FileSystemLoader("templates"))


@app.get("/", response_class=HTMLResponse)
async def home():
    template = templates.get_template("index.html")
    return template.render()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def running():
    if chzzk.has_credentials():
        bot_profile = await chzzk.me()
        if bot_profile.logged_in is False:
            _log.error(f"현재 입력하신 로그인 정보는 만료되었습니다. 다시 로그인해주세요.")
            chzzk._credential = None
        else:
            _log.info(f"{bot_profile.nickname} 계정으로 로그인 합니다.")

    await chzzk_chat.run(channel_id=get_env("channel_id"))


def main():
    asyncio.run(running())


@chzzk_chat.event
async def on_connect():
    channel = await chzzk.channel(get_env("channel_id"))
    _log.info(f"{channel.channel_name} 채널에 성공적으로 접속했습니다.")


@chzzk_chat.event
async def on_chat(message: ChatMessage):
    # 이모티콘은 {:d_1:} 이렇게 뜸 {: ... :}을 체크해서 지우기
    await tts.create_tts(message.user_id, message.content, manager)
    _log.info(f"{message.profile.nickname}: {message.content}")


if __name__ == "__main__":
    thread = Thread(target=main, daemon=True)
    thread.start()
    _log.info("http://localhost:5005를 클릭하여 브라우저를 띄운 후, 흰 화면을 클릭해주셔야 정상 작동합니다.")
    uvicorn.run(app, host="localhost", port=5005)
    input("Press Enter to exit...")