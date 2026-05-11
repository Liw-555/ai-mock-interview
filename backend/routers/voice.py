"""
Voice TTS / STT API.
Uses edge-tts for text-to-speech (free, no API key).
Uses Web Speech API on frontend for STT (browser built-in).
"""

import io
import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    voice: str = "zh-CN-XiaoxiaoNeural"  # 晓晓（女声，自然）


@router.post("/tts")
async def text_to_speech(req: TTSRequest):
    """Convert text to speech using edge-tts."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty")

    try:
        import edge_tts
        communicate = edge_tts.Communicate(req.text, voice=req.voice)
        mp3_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                mp3_buffer.write(chunk["data"])
        mp3_buffer.seek(0)
        return StreamingResponse(mp3_buffer, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


@router.get("/voices")
async def list_voices():
    """List available Chinese voices."""
    return {
        "zh-CN-XiaoxiaoNeural": "晓晓（女声，自然）",
        "zh-CN-YunyangNeural": "云扬（男声，新闻）",
        "zh-CN-YunxiNeural": "云希（男声，活泼）",
        "zh-CN-XiaoyiNeural": "晓伊（女声，温柔）",
    }
