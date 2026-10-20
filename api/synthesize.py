from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import edge_tts

app = FastAPI()

VOICES = {
    "mohan": "te-IN-MohanNeural",
    "shruti": "te-IN-ShrutiNeural"
}

@app.post("/")
@app.post("/api/synthesize")
async def synthesize_telugu(payload: dict):
    text = payload.get("text", "").strip()
    voice_key = payload.get("voice", "mohan")
    rate = payload.get("rate", "+0%")

    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    selected_voice = VOICES.get(voice_key, "te-IN-MohanNeural")

    try:
        communicate = edge_tts.Communicate(text, voice=selected_voice, rate=rate)
        audio_data = bytearray()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])

        return Response(content=bytes(audio_data), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))