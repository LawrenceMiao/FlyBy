import React, { useEffect, useRef } from "react";
import Hls from "hls.js";

const VideoPlayer: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    if (Hls.isSupported() && videoRef.current) {
      const hls = new Hls();
      hls.loadSource("http://carpi.cs.rpi.edu:8000/stream");
      hls.attachMedia(videoRef.current);
    }
  }, []);

  return (
    <div className="w-full h-full flex justify-center items-center">
      <video ref={videoRef} controls className="w-full h-full object-cover rounded" />
    </div>
  );
};

export default VideoPlayer;