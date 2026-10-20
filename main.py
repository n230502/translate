from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
import edge_tts
import asyncio
import os

app = FastAPI()

VOICES = {
    "mohan": "te-IN-MohanNeural",
    "shruti": "te-IN-ShrutiNeural"
}

@app.get("/")
async def serve_frontend():
    if os.path.exists("public/index.html"):
        return FileResponse("public/index.html")
    elif os.path.exists("index.html"):
        return FileResponse("index.html")
    raise HTTPException(status_code=404, detail="index.html not found")

@app.post("/api/synthesize")
async def synthesize_telugu(payload: dict):
    text = payload.get("text", "").strip()
    voice_key = payload.get("voice", "mohan")
    rate = payload.get("rate", "+0%")

    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    selected_voice = VOICES.get(voice_key, "te-IN-MohanNeural")

    # Automatically retry up to 5 times behind the scenes
    MAX_ATTEMPTS = 5
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            communicate = edge_tts.Communicate(text, voice=selected_voice, rate=rate)
            audio_data = bytearray()

            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.extend(chunk["data"])

            # If audio was successfully received, return it immediately
            if len(audio_data) > 0:
                return Response(content=bytes(audio_data), media_type="audio/mpeg")

        except Exception as e:
            last_error = e
            # Wait briefly before retrying (0.4s, 0.8s, etc.)
            await asyncio.sleep(0.4 * attempt)

    # If all 5 attempts fail, return error
    raise HTTPException(
        status_code=500, 
        detail=f"Speech synthesis failed after {MAX_ATTEMPTS} attempts: {str(last_error)}"
    )
