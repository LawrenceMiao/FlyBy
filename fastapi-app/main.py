import os
import subprocess

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

_UPLOAD_DIR = "uploads"
_STATIC_DIR = "static"
os.makedirs(_UPLOAD_DIR, exist_ok=True)
os.makedirs(_STATIC_DIR, exist_ok=True)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.post("/upload")
def upload_video(file: UploadFile):
    buf_location = os.path.join(_UPLOAD_DIR, file.filename)
    with open(buf_location, "wb") as buf:
        buf.write(file.file.read())
    cmd = [
        "ffmpeg",
        "-i",
        buf_location,
        "-profile:v",
        "baseline",  # Broad compatibility
        "-level",
        "3.0",
        "-start_number",
        "0",  # Start segment index at 0
        "-hls_time",
        "10",  # 10-second segments
        "-hls_list_size",
        "0",  # Keep all segments in the manifest
        "-f",
        "hls",
        os.path.join(_STATIC_DIR, "playlist.m3u8"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"FFmpeg failed: {result.stderr}")
    return 200


@app.get("/stream")
def play_video():
    return FileResponse(os.path.join(_STATIC_DIR, "playlist.m3u8"))
