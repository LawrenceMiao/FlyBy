import React, { useState , useEffect, useRef } from "react";
import Hls from "hls.js";
import { UploadIcon, CheckCircledIcon } from "@radix-ui/react-icons";

interface VideoPlayerProps {
  setData: (data: any) => void;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ setData }) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const hlsInstance = useRef<Hls | null>(null);

  const [_, setVideoAvailable] = useState<boolean>(false);
  const [videoLoaded, setVideoLoaded] = useState<boolean>(false);
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [UIUD, setUIUD] = useState<string>("");

  const API_BASE_URL = "http://74.70.76.86:8000";

  // HLS STREAMING
  useEffect(() => {
    console.log("Component mounted, calling stream...");
    console.log(UIUD);

    const video = videoRef.current;
    if (!video || UIUD === "") return;

    // Loads the HLS Stream
    const loadHlsStream = () => {
      if (Hls.isSupported()) {
        if (hlsInstance.current) {
          hlsInstance.current.destroy();
        }

        const hls = new Hls({ debug: false });
        hlsInstance.current = hls;

        // creating stream URL for the video
        const streamUrl = API_BASE_URL + "/stream/" + UIUD;
        hls.loadSource(streamUrl);
        hls.attachMedia(video);

        // HLS events
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          console.log("HLS manifest loaded successfully.");
          setVideoAvailable(true);
          loadData();
          video.play().catch(error => console.warn("Autoplay blocked:", error));
        });

        hls.on(Hls.Events.ERROR, (_, data) => {
          console.error("HLS.js error:", data);
          setVideoAvailable(false);
        });
      } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
        video.src = API_BASE_URL + "/stream/" + UIUD;
        video.load();
        loadData();
      }
    };

    // Loads the Data returned from the Model
    const loadData = async () => {
      const response = await fetch(API_BASE_URL + "/data/" + UIUD);
      const data = await response.json();
      setData(data);
    }

    loadHlsStream();

    return () => {
      if (hlsInstance.current) {
        hlsInstance.current.destroy();
      }
    };
  }, [videoLoaded, UIUD]);

  // FILE UPLOADING
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedVideo(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedVideo) return;

    setVideoLoaded(true);

    const formData = new FormData();
    formData.append("file", selectedVideo);

    try {
      const response = await fetch(API_BASE_URL + "/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        const videoUuid = data.video_uuid;
        setUIUD(videoUuid);
        console.log("Upload successful");
      } else {
        console.error("Upload failed");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  return (
    <div className="w-full h-full flex flex-col justify-center items-center">
      {videoLoaded ? (
        <video
          ref={videoRef}
          controls
          muted
          className="relative z-50 pointer-events-auto w-full h-full object-cover rounded"
        />
      ) : (
        <div className="relative z-50 pointer-events-auto flex flex-col items-center border-2 border-dashed p-6 rounded-lg">
          <p className="text-gray-500 mb-2">No video available. Upload one!</p>
          
          <div className="m-4">
            <label htmlFor="file-upload" className="flex flex-col items-center cursor-pointer">
              {selectedVideo != null ? <CheckCircledIcon className="h-12 w-12 text-gray-400 mb-2"/> : <UploadIcon className="h-12 w-12 text-gray-400 mb-2" />}
              <span className="text-sm text-gray-500">{selectedVideo != null ? "Video Loaded" : "Click to upload"}</span>
            </label>
            <input
              id="file-upload"
              type="file"
              accept="video/mp4,video/mkv,video/quicktime"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>

          <button
            onClick={handleUpload}
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700"
            disabled={!selectedVideo}
          >
            Upload Video
          </button>
        </div>
      )}
    </div>
  );
};

export default VideoPlayer;