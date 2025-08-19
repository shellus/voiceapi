from typing import *
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import logging
from pydantic import BaseModel, Field
import uvicorn
from voiceapi.tts import TTSResult, start_tts_stream, TTSStream
from voiceapi.asr import start_asr_stream, ASRStream, ASRResult, load_asr_engine
import logging
import argparse
import os

app = FastAPI()
logger = logging.getLogger(__file__)

# 全局ASR引擎，在启动时预加载
_asr_engine = None


@app.websocket("/asr")
async def websocket_asr(websocket: WebSocket,
                        samplerate: int = Query(16000, title="Sample Rate",
                                                description="The sample rate of the audio."),):
    await websocket.accept()
    logger.info("connection open")

    # 使用预加载的ASR引擎创建流
    if not _asr_engine:
        logger.error("ASR engine not loaded")
        await websocket.close()
        return

    asr_stream = ASRStream(_asr_engine, samplerate)
    await asr_stream.start()

    async def task_recv_pcm():
        # 直接接收音频数据（字节）
        while True:
            try:
                pcm_bytes = await websocket.receive_bytes()
                if not pcm_bytes:
                    return
                await asr_stream.write(pcm_bytes)
            except Exception as e:
                logger.error(f"asr: error receiving audio data: {e}")
                return

    async def task_send_result():
        while True:
            result: ASRResult = await asr_stream.read()
            if not result:
                return
            await websocket.send_json(result.to_dict())
    try:
        await asyncio.gather(task_recv_pcm(), task_send_result())
    except WebSocketDisconnect:
        logger.info("asr: disconnected")
    finally:
        await asr_stream.close()


@app.websocket("/tts")
async def websocket_tts(websocket: WebSocket,
                        samplerate: int = Query(16000,
                                                title="Sample Rate",
                                                description="The sample rate of the generated audio."),
                        interrupt: bool = Query(True,
                                                title="Interrupt",
                                                description="Interrupt the current TTS stream when a new text is received."),
                        sid: int = Query(0,
                                         title="Speaker ID",
                                         description="The ID of the speaker to use for TTS."),
                        chunk_size: int = Query(1024,
                                                title="Chunk Size",
                                                description="The size of the chunk to send to the client."),
                        speed: float = Query(1.0,
                                             title="Speed",
                                             description="The speed of the generated audio."),
                        split: bool = Query(True,
                                            title="Split",
                                            description="Split the text into sentences.")):

    await websocket.accept()
    tts_stream: TTSStream = None

    async def task_recv_text():
        nonlocal tts_stream
        while True:
            text = await websocket.receive_text()
            if not text:
                return

            if interrupt or not tts_stream:
                if tts_stream:
                    await tts_stream.close()
                    logger.info("tts: stream interrupt")

                tts_stream = await start_tts_stream(sid, samplerate, speed, args)
                if not tts_stream:
                    logger.error("tts: failed to allocate tts stream")
                    await websocket.close()
                    return
            logger.info(f"tts: received: {text} (split={split})")
            await tts_stream.write(text, split)

    async def task_send_pcm():
        nonlocal tts_stream
        while not tts_stream:
            # wait for tts stream to be created
            await asyncio.sleep(0.1)

        while True:
            result: TTSResult = await tts_stream.read()
            if not result:
                return

            if result.finished:
                await websocket.send_json(result.to_dict())
            else:
                for i in range(0, len(result.pcm_bytes), chunk_size):
                    await websocket.send_bytes(result.pcm_bytes[i:i+chunk_size])

    try:
        await asyncio.gather(task_recv_text(), task_send_pcm())
    except WebSocketDisconnect:
        logger.info("tts: disconnected")
    finally:
        if tts_stream:
            await tts_stream.close()


class TTSRequest(BaseModel):
    text: str = Field(..., title="Text",
                      description="The text to be converted to speech.",
                      examples=["Hello, world!"])
    sid: int = Field(0, title="Speaker ID",
                     description="The ID of the speaker to use for TTS.")
    samplerate: int = Field(16000, title="Sample Rate",
                            description="The sample rate of the generated audio.")
    speed: float = Field(1.0, title="Speed",
                         description="The speed of the generated audio.")


@ app.post("/tts",
           description="Generate speech audio from text.",
           response_class=StreamingResponse, responses={200: {"content": {"audio/wav": {}}}})
async def tts_generate(req: TTSRequest):
    if not req.text:
        raise HTTPException(status_code=400, detail="text is required")

    tts_stream = await start_tts_stream(req.sid, req.samplerate, req.speed,  args)
    if not tts_stream:
        raise HTTPException(
            status_code=500, detail="failed to start TTS stream")

    r = await tts_stream.generate(req.text)
    return StreamingResponse(r, media_type="audio/wav")


if __name__ == "__main__":
    models_root = './models'

    for d in ['.', '..', '../..']:
        if os.path.isdir(f'{d}/models'):
            models_root = f'{d}/models'
            break

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000, help="port number")
    parser.add_argument("--addr", type=str,
                        default="0.0.0.0", help="serve address")

    parser.add_argument("--asr-provider", type=str,
                        default="cpu", help="asr provider, cpu or cuda")
    parser.add_argument("--tts-provider", type=str,
                        default="cpu", help="tts provider, cpu or cuda")

    parser.add_argument("--threads", type=int, default=2,
                        help="number of threads")

    parser.add_argument("--models-root", type=str, default=models_root,
                        help="model root directory")

    parser.add_argument("--asr-model", type=str, default='sensevoice',
                        help="ASR model name: zipformer-bilingual, sensevoice, paraformer-trilingual, paraformer-en, fireredasr")

    parser.add_argument("--asr-lang", type=str, default='zh',
                        help="ASR language, zh, en, ja, ko, yue")

    parser.add_argument("--tts-model", type=str, default='vits-zh-hf-theresa',
                        help="TTS model name: vits-zh-hf-theresa, vits-melo-tts-zh_en, kokoro-multi-lang-v1_0")

    args = parser.parse_args()

    if args.tts_model == 'vits-melo-tts-zh_en' and args.tts_provider == 'cuda':
        logger.warning(
            "vits-melo-tts-zh_en does not support CUDA fallback to CPU")
        args.tts_provider = 'cpu'

    # 添加启动事件处理器
    async def startup_event():
        """应用启动时预加载ASR引擎"""
        global _asr_engine
        logger.info("正在预加载ASR引擎...")
        _asr_engine = load_asr_engine(16000, args)
        logger.info("ASR引擎预加载完成")

    app.add_event_handler("startup", startup_event)
    app.mount("/", app=StaticFiles(directory="./assets", html=True), name="assets")

    logging.basicConfig(format='%(levelname)s: %(asctime)s %(name)s:%(lineno)s %(message)s',
                        level=logging.INFO)
    uvicorn.run(app, host=args.addr, port=args.port)
