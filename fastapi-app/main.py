import os
import re
import subprocess

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

_UPLOAD_DIR = "uploads"
_STATIC_DIR = "static"
_HLS_DIR = os.path.join(_STATIC_DIR, "hls")
os.makedirs(_UPLOAD_DIR, exist_ok=True)
os.makedirs(_STATIC_DIR, exist_ok=True)
os.makedirs(_HLS_DIR, exist_ok=True)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.mount("/hls", StaticFiles(directory=_HLS_DIR), name="hls")


def _get_ffmpeg_command(input_file: str, output_manifest_file: str) -> list[str]:
    return [
        "ffmpeg",
        "-i",
        input_file,
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
        output_manifest_file,
    ]


def _clear_directory(dir: str) -> None:
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))


@app.post("/upload")
def upload_video(file: UploadFile):
    _clear_directory(_UPLOAD_DIR)
    _clear_directory(_HLS_DIR)
    buf_location = os.path.join(_UPLOAD_DIR, file.filename)
    with open(buf_location, "wb") as buf:
        buf.write(file.file.read())
    cmd = _get_ffmpeg_command(buf_location, os.path.join(_HLS_DIR, "playlist.m3u8"))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"FFmpeg failed: {result.stderr}")
    return 200


@app.get("/stream")
def get_manifest():
    video_segment_regex = re.compile(r"(.*.ts)\n")
    manifest_content = None
    with open(os.path.join(_HLS_DIR, "playlist.m3u8"), "r") as manifest:
        manifest_content = manifest.read()
    manifest_content = re.sub(video_segment_regex, "hls/\\1\n", manifest_content)
    return Response(
        content=manifest_content, media_type="application/vnd.apple.mpegurl"
    )
