import UploadPanel from "../components/UploadPanel";
import VideoUploadPanel from "../components/VideoUploadPanel";
import WebcamCapture from "../components/WebcamCapture";

export default function LiveDetect() {
  return (
    <div className="p-8 space-y-8">
      <h1 className="text-2xl font-semibold text-slate-800">Live Emotion Detection</h1>
      <UploadPanel />
      <VideoUploadPanel />
      <WebcamCapture />
    </div>
  );
}