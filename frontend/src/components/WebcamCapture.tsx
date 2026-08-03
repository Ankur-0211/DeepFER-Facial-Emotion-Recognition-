import { useRef, useState, useEffect } from "react";
import { useWebSocketStream } from "../hooks/useWebSocket";

export default function WebcamCapture() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [active, setActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { connect, disconnect, sendFrame, predictions } = useWebSocketStream();

  async function startWebcam() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) videoRef.current.srcObject = stream;
      connect();
      setActive(true);
    } catch {
      setError("Could not access webcam. Check browser permissions.");
    }
  }

  function stopWebcam() {
    const stream = videoRef.current?.srcObject as MediaStream | null;
    stream?.getTracks().forEach((track) => track.stop());
    disconnect();
    setActive(false);
  }

  // Send a frame to the backend every 500ms while active (throttled per SDD NFR guidance)
  useEffect(() => {
    if (!active) return;
    const interval = setInterval(() => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (!video || !canvas) return;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx?.drawImage(video, 0, 0);
      canvas.toBlob((blob) => blob && sendFrame(blob), "image/jpeg", 0.8);
    }, 500);
    return () => clearInterval(interval);
  }, [active, sendFrame]);

  return (
    <div className="border rounded-xl p-6 bg-white shadow-sm">
      <h2 className="text-lg font-medium text-slate-800 mb-3">Live webcam</h2>
      <video ref={videoRef} autoPlay muted className="w-full max-w-md rounded-lg bg-black" />
      <canvas ref={canvasRef} className="hidden" />
      <div className="mt-3 space-x-2">
        {!active ? (
          <button onClick={startWebcam} className="bg-slate-800 text-white px-4 py-2 rounded-lg">
            Start webcam
          </button>
        ) : (
          <button onClick={stopWebcam} className="bg-red-600 text-white px-4 py-2 rounded-lg">
            Stop webcam
          </button>
        )}
      </div>
      {error && <p className="text-red-600 text-sm mt-2">{error}</p>}
      {predictions.length > 0 && (
        <ul className="mt-3">
          {predictions.map((p, i) => (
            <li key={i} className="text-slate-700">
              {p.emotion} — {(p.confidence * 100).toFixed(0)}%
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}