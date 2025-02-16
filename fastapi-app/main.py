import os
import re
import shutil
import subprocess
import uuid

import detector
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

_UPLOADS_DIR = "temp-uploads"
_ANALYZED_DIR = "temp-analyzed"
_STATIC_DIR = "static"
_HLS_DIR = os.path.join(_STATIC_DIR, "hls")
shutil.rmtree(_UPLOADS_DIR, ignore_errors=True)
shutil.rmtree(_ANALYZED_DIR, ignore_errors=True)
shutil.rmtree(_STATIC_DIR, ignore_errors=True)
shutil.rmtree(_HLS_DIR, ignore_errors=True)
os.makedirs(_UPLOADS_DIR, exist_ok=True)
os.makedirs(_ANALYZED_DIR, exist_ok=True)
os.makedirs(_STATIC_DIR, exist_ok=True)
os.makedirs(_HLS_DIR, exist_ok=True)

_VIDEO_MANIFEST_NAME = "playlist.m3u8"


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.mount("/hls", StaticFiles(directory=_HLS_DIR), name="hls")


def _get_ffmpeg_command(input_path: str, output_manifest_path: str) -> list[str]:
    return [
        "ffmpeg",
        "-i",
        input_path,
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
        output_manifest_path,
    ]


@app.post("/upload")
def upload_video(file: UploadFile) -> dict[str, str]:
    # Save uploaded video to storage
    temp_video_path = os.path.join(_UPLOADS_DIR, file.filename)
    with open(temp_video_path, "wb") as buf:
        buf.write(file.file.read())

    # Analyze video for garbage
    temp_analyzed_video_path = os.path.join(_ANALYZED_DIR, file.filename)
    garbage_stats = detector.process_video(
        temp_video_path, temp_analyzed_video_path
    )
    os.remove(temp_video_path)

    # Create unique directory for processed video segments
    video_uuid = str(uuid.uuid4())
    video_dir = os.path.join(_HLS_DIR, video_uuid)
    os.makedirs(video_dir, exist_ok=True)
    video_manifest_path = os.path.join(video_dir, _VIDEO_MANIFEST_NAME)
    cmd = _get_ffmpeg_command(temp_analyzed_video_path, video_manifest_path)
    result = subprocess.run(cmd, capture_output=True, text=True)
    os.remove(temp_analyzed_video_path)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"FFmpeg failure")
    
    return {"hls_manifest": f"/stream/{video_uuid}"}


@app.get("/stream/{video_uuid}")
def get_manifest(video_uuid: str):
    video_dir = os.path.join(_HLS_DIR, video_uuid)
    if not os.path.exists(video_dir) or len(os.listdir(video_dir)) == 0 or _VIDEO_MANIFEST_NAME not in os.listdir(video_dir):
        return HTTPException(status_code=404, detail="Video not found")
    video_segment_regex = re.compile(r"(.*.ts)\n")
    video_manifest_path = os.path.join(video_dir, _VIDEO_MANIFEST_NAME)
    manifest_content = None
    try:
        with open(video_manifest_path, "r") as manifest_file:
            manifest_content = manifest_file.read()
    except OSError:
        return HTTPException(status_code=500, detail="Failed to read video manifest")
    # Replace inaccurate relative video segment paths with correct absolute paths
    manifest_content = re.sub(video_segment_regex, f"hls/{video_uuid}/\\1\n", manifest_content)
    return Response(
        content=manifest_content, media_type="application/vnd.apple.mpegurl"
    )
