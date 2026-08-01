import { useRef, useState } from "react";

export default function WebcamCapture() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [active, setActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function startWebcam() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setActive(true);
    } catch {
      setError("Could not access webcam. Check browser permissions.");
    }
  }

  function stopWebcam() {
    const stream = videoRef.current?.srcObject as MediaStream | null;
    stream?.getTracks().forEach((track) => track.stop());
    setActive(false);
  }

  return (
    <div className="border rounded-xl p-6 bg-white shadow-sm">
      <h2 className="text-lg font-medium text-slate-800 mb-3">Live webcam</h2>
      <video ref={videoRef} autoPlay muted className="w-full max-w-md rounded-lg bg-black" />
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
    </div>
  );
}