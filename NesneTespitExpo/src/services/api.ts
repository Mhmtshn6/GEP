import axios from "axios";
import { API_BASE_URL, DETECT_ENDPOINT, HEALTH_ENDPOINT, REQUEST_TIMEOUT } from "../constants";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
});

export interface DetectedObject {
  label_en:   string;
  label_tr:   string;
  confidence: number;
  position:   "sol" | "orta" | "sağ";
  distance:   string;
  bbox: { x1: number; y1: number; x2: number; y2: number };
}

export interface DetectionResponse {
  objects:     DetectedObject[];
  speech_text: string;
  frame_ms:    number;
  total_ms:    number;
}

export async function detectObjects(base64Image: string): Promise<DetectionResponse> {
  const formData = new FormData();
  formData.append("image", {
    uri:  `data:image/jpeg;base64,${base64Image}`,
    name: "frame.jpg",
    type: "image/jpeg",
  } as any);

  const response = await client.post<DetectionResponse>(DETECT_ENDPOINT, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await client.get(HEALTH_ENDPOINT);
    return response.data.model_ready === true;
  } catch {
    return false;
  }
}
