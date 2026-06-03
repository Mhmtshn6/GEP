// ── API ────────────────────────────────────────────────────────────────────────
export const API_BASE_URL    = "http://192.168.137.1:8000";
export const DETECT_ENDPOINT = "/detect";
export const HEALTH_ENDPOINT = "/health";
export const REQUEST_TIMEOUT = 5000;

// ── Frame yakalama ─────────────────────────────────────────────────────────────
export const FRAME_INTERVAL_MS = 1000;  // 1 saniyede bir — yolov8s biraz daha yavaş
export const JPEG_QUALITY      = 0.8;  // Kaliteyi artırdık — daha iyi tespit

// ── TTS ────────────────────────────────────────────────────────────────────────
export const TTS_COOLDOWN_MS = 3000;   // Aynı nesne 3 saniyede bir tekrar söylenir
