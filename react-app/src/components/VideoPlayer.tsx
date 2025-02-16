import React, { useEffect, useRef } from "react";
import Hls from "hls.js";

const VideoPlayer: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const hlsInstance = useRef<Hls | null>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    if (Hls.isSupported()) {
      if (hlsInstance.current) {
        hlsInstance.current.destroy();
      }

      const hls = new Hls({ debug: false });
      hlsInstance.current = hls;
      hls.loadSource("http://carpi.cs.rpi.edu:8000/stream");
      hls.attachMedia(video);

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        console.log("HLS manifest loaded successfully.");
        video.play().catch(error => console.warn("Autoplay blocked:", error));
      });

      hls.on(Hls.Events.ERROR, (event, data) => {
        console.error("HLS.js error:", data);
      });
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = "http://carpi.cs.rpi.edu:8000/stream";
      video.load();
    }

    return () => {
      if (hlsInstance.current) {
        hlsInstance.current.destroy();
      }
    };
  }, []);

  return (
    <div className="w-full h-full flex justify-center items-center">
      <video
        ref={videoRef}
        controls
        muted
        className="relative z-50 pointer-events-auto w-full h-full object-cover rounded"
      />
    </div>
  );
};

export default VideoPlayer;