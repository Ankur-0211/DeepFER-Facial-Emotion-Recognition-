import { useRef, useCallback, useState } from "react";
import type { EmotionPrediction } from "../types";
import { API_BASE_URL } from "../services/apiClient";
import { getAccessToken } from "../services/tokenStore";

export function useWebSocketStream() {
  const wsRef = useRef<WebSocket | null>(null);
  const [predictions, setPredictions] = useState<EmotionPrediction[]>([]);
  const [connected, setConnected] = useState(false);

  const connect = useCallback(() => {
    const token = getAccessToken() ?? "";
    const wsUrl = `${API_BASE_URL.replace(/^http/, "ws")}/ws/v1/stream?token=${token}`;
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.predictions) setPredictions(data.predictions);
    };
    wsRef.current = ws;
  }, []);

  const sendFrame = useCallback((blob: Blob) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      blob.arrayBuffer().then((buf) => wsRef.current?.send(buf));
    }
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
  }, []);

  return { connect, disconnect, sendFrame, predictions, connected };
}