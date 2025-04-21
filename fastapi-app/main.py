import json
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

_UPLOADS_DIR = os.path.abspath("temp-uploads")
_ANALYZED_DIR = os.path.abspath("temp-analyzed")
_STATIC_DIR = os.path.abspath("static")
_HLS_DIR = os.path.join(_STATIC_DIR, "hls")
_DATA_DIR = os.path.join(_STATIC_DIR, "data")
_VIDEO_MANIFEST_NAME = "playlist.m3u8"

# Clean temporary storage
shutil.rmtree(_UPLOADS_DIR, ignore_errors=True)
os.makedirs(_UPLOADS_DIR, exist_ok=True)
shutil.rmtree(_ANALYZED_DIR, ignore_errors=True)
os.makedirs(_ANALYZED_DIR, exist_ok=True)
shutil.rmtree(_STATIC_DIR, ignore_errors=True)
os.makedirs(_STATIC_DIR, exist_ok=True)
shutil.rmtree(_HLS_DIR, ignore_errors=True)
os.makedirs(_HLS_DIR, exist_ok=True)
shutil.rmtree(_DATA_DIR, ignore_errors=True)
os.makedirs(_DATA_DIR, exist_ok=True)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
# Make HLS video segments publicly accessible at /stream/hls
app.mount("/stream/hls", StaticFiles(directory=_HLS_DIR), name="hls")


def _get_ffmpeg_command(input_path: str, output_manifest_path: str) -> list[str]:
    return [
        "ffmpeg",
        "-i",
        input_path,
        "-profile:v",
        "baseline",
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


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple endpoint to verify the API is online and responding."""
    return {"status": "online", "message": "API is running"}


@app.post("/upload")
def upload_process_video(file: UploadFile) -> dict[str, str]:
    # Save uploaded video to storage
    temp_video_path = os.path.join(_UPLOADS_DIR, file.filename)
    with open(temp_video_path, "wb") as buf:
        buf.write(file.file.read())

    # Analyze video for garbage
    temp_analyzed_video_path = os.path.join(_ANALYZED_DIR, file.filename)
    video_garbage_data = detector.process_video(
        temp_video_path, temp_analyzed_video_path
    )
    os.remove(temp_video_path)
    if not os.path.exists(temp_analyzed_video_path):
        raise HTTPException(status_code=500, detail="Failed to analyze video")

    # Generate unique identifier for video
    video_uuid = str(uuid.uuid4())

    # Save video garbage data to storage
    video_garbage_data_path = os.path.join(_DATA_DIR, f"{video_uuid}.json")
    with open(video_garbage_data_path, "w") as data_file:
        json.dump(video_garbage_data, data_file)

    # Create unique directory for processed video segments
    video_dir = os.path.join(_HLS_DIR, video_uuid)
    os.makedirs(video_dir, exist_ok=True)
    video_manifest_path = os.path.join(video_dir, _VIDEO_MANIFEST_NAME)

    # Use ffmpeg to segment video for HLS streaming
    cmd = _get_ffmpeg_command(temp_analyzed_video_path, video_manifest_path)
    result = subprocess.run(cmd, capture_output=True, text=True)
    os.remove(temp_analyzed_video_path)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"FFmpeg failed")

    return {"video_uuid": video_uuid}


@app.get("/stream/{video_uuid}")
def get_video_manifest(video_uuid: str) -> str:
    # Sanity check
    video_dir = os.path.join(_HLS_DIR, video_uuid)
    if (
        not os.path.exists(video_dir)
        or len(os.listdir(video_dir)) == 0
        or _VIDEO_MANIFEST_NAME not in os.listdir(video_dir)
    ):
        return HTTPException(status_code=404, detail="Video not found")

    video_manifest_path = os.path.join(video_dir, _VIDEO_MANIFEST_NAME)
    manifest_content = None
    try:
        with open(video_manifest_path, "r") as manifest_file:
            manifest_content = manifest_file.read()
    except OSError:
        return HTTPException(status_code=500, detail="Failed to read video manifest")

    # Replace inaccurate relative video segment paths with correct absolute paths
    video_segment_regex = re.compile(r"(.*.ts)\n")
    manifest_content = re.sub(
        video_segment_regex, f"hls/{video_uuid}/\\1\n", manifest_content
    )

    return Response(
        content=manifest_content, media_type="application/vnd.apple.mpegurl"
    )


@app.get("/data/{video_uuid}")
def get_video_garbage_data(video_uuid: str) -> dict[str, int | dict[str, int]]:
    # Sanity check
    video_dir = os.path.join(_HLS_DIR, video_uuid)
    if (
        not os.path.exists(video_dir)
        or len(os.listdir(video_dir)) == 0
        or _VIDEO_MANIFEST_NAME not in os.listdir(video_dir)
    ):
        return HTTPException(status_code=404, detail="Video not found")

    video_garbage_data_path = os.path.join(_DATA_DIR, f"{video_uuid}.json")
    garbage_data = None
    try:
        with open(video_garbage_data_path, "r") as data_file:
            garbage_data = json.load(data_file)
    except OSError:
        return HTTPException(
            status_code=500, detail="Failed to read video garbage data"
        )

    return garbage_data
