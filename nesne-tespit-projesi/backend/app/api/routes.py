"""
routes.py
---------
Görme engelli için kritik nesnelere odaklanır.
Düşük confidence ve alakasız nesneler filtrelenir.
"""

import logging
import time

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.core.detector import detector

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

# ── Görme engelli için kritik COCO nesneleri ──────────────────────────────────
# Bunların dışındaki tespitler filtrelenir — yanlış tahmin yerine sessiz kal
CRITICAL_LABELS = {
    # Trafik / dış mekan
    "person",       # insan
    "car",          # araba
    "bus",          # otobüs
    "truck",        # kamyon
    "motorcycle",   # motosiklet
    "bicycle",      # bisiklet
    "traffic light",# trafik ışığı
    "stop sign",    # dur tabelası
    "bench",        # bank
    # İç mekan engelleri
    "chair",        # sandalye
    "couch",        # kanepe
    "bed",          # yatak
    "dining table", # masa
    "toilet",       # tuvalet
    "door",         # kapı (COCO'da yok ama gelirse yakalasın)
    "stairs",       # merdiven
    # Hayvanlar
    "dog",          # köpek
    "cat",          # kedi
    "horse",        # at
    # Günlük nesneler
    "bottle",       # şişe
    "cup",          # bardak
    "laptop",       # dizüstü
    "tv",           # televizyon
    "cell phone",   # telefon
    "backpack",     # sırt çantası
    "umbrella",     # şemsiye
    "suitcase",     # bavul
}

@router.post("/detect")
async def detect_objects(image: UploadFile = File(...)):
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail=f"Desteklenmeyen format: {image.content_type}")

    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Görüntü 10MB'ı aşıyor.")

    t0 = time.perf_counter()
    try:
        result = detector.detect(image_bytes)
    except Exception as e:
        logger.exception("Tespit sırasında hata")
        raise HTTPException(status_code=500, detail=f"Tespit hatası: {str(e)}")

    # ── Kritik nesne filtresi ─────────────────────────────────────────────────
    # Sadece CRITICAL_LABELS içindeki nesneleri döndür
    filtered = [
        obj for obj in result["objects"]
        if obj["label_en"] in CRITICAL_LABELS
    ]

    # Speech text'i filtrelenmiş nesnelerden yeniden üret
    from app.core.postprocess import build_speech_text
    speech_text = build_speech_text(filtered)

    total_ms = int((time.perf_counter() - t0) * 1000)

    response = {
        "objects":     filtered,
        "speech_text": speech_text,
        "frame_ms":    result["frame_ms"],
        "total_ms":    total_ms,
    }

    logger.debug(
        f"Tespit tamamlandı: {len(filtered)} nesne "
        f"({len(result['objects'])} ham → {len(filtered)} filtreli), "
        f"{total_ms}ms"
    )

    return JSONResponse(content=response)


@router.get("/health")
async def health_check():
    model_ready = detector._model is not None
    return {
        "status":      "ok" if model_ready else "model_not_loaded",
        "model_ready": model_ready,
    }
