"""
detector.py
-----------
YOLOv8 modelini yükler ve görüntü üzerinde nesne tespiti yapar.

Tasarım kararları:
  - Model uygulama başlarken bir kez yüklenir (singleton pattern).
    Her request'te yeniden yüklenmesi ciddi gecikmeye neden olur.
  - Görüntü gelmeden önce boyut normalize edilir (max_size x max_size).
    Bu hem hızı artırır hem de tutarlı konum hesabı sağlar.
  - Tüm post-processing postprocess.py modülüne delege edilir.
"""

import io
import logging
from pathlib import Path

import numpy as np
from PIL import Image
from ultralytics import YOLO

from app.config import get_settings
from app.core.postprocess import BoundingBox, get_position, get_distance, build_speech_text
from app.core.translator import translate

logger = logging.getLogger(__name__)


class ObjectDetector:
    """
    YOLOv8 tabanlı nesne tespit motoru.
    FastAPI lifespan event'inde bir kez başlatılır.
    """

    def __init__(self) -> None:
        self._model: YOLO | None = None
        self._settings = get_settings()

    def load(self) -> None:
        """
        Modeli diske yükler. Uygulama startup'ında çağrılır.
        Model dosyası yoksa Ultralytics otomatik indirir.
        """
        model_path = Path(self._settings.model_path)
        logger.info(f"Model yükleniyor: {model_path}")

        self._model = YOLO(str(model_path))

        # İlk warmup çağrısı: model ilk çalışmada daha yavaş olur,
        # bunu startup'a taşıyarak ilk kullanıcı isteğinin gecikmesini önleriz.
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        self._model(dummy, verbose=False)

        logger.info("Model hazır, warmup tamamlandı.")

    def detect(self, image_bytes: bytes) -> dict:
        """
        Ham görüntü byte'larını alır, tespit sonuçlarını döner.

        Parametreler
        ------------
        image_bytes : bytes
            JPEG / PNG formatında görüntü verisi

        Döner
        -----
        dict
            {
              "objects": [...],          # Tespit listesi
              "speech_text": str,        # TTS için hazır Türkçe metin
              "frame_ms": int            # Inference süresi (ms)
            }
        """
        if self._model is None:
            raise RuntimeError("Dedektör başlatılmamış. load() çağrıldı mı?")

        settings = self._settings

        # 1. Görüntüyü numpy array'e çevir ve boyutlandır
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = self._resize(img, settings.max_image_size)
        img_array = np.array(img)
        img_h, img_w = img_array.shape[:2]

        # 2. Inference
        results = self._model(
            img_array,
            conf=settings.confidence_threshold,
            iou=settings.iou_threshold,
            verbose=False,
        )

        # 3. Sonuçları işle
        detections = []
        result = results[0]  # Batch'in ilk (ve tek) elemanı

        if result.boxes is not None:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf   = float(box.conf[0])
                cls_id = int(box.cls[0])
                label_en = result.names[cls_id]
                label_tr = translate(label_en)

                bbox = BoundingBox(
                    x1=x1, y1=y1, x2=x2, y2=y2,
                    img_width=img_w, img_height=img_h,
                )

                detections.append({
                    "label_en":   label_en,
                    "label_tr":   label_tr,
                    "confidence": round(conf, 3),
                    "position":   get_position(bbox),
                    "distance":   get_distance(bbox),
                    "bbox": {
                        "x1": round(x1), "y1": round(y1),
                        "x2": round(x2), "y2": round(y2),
                    },
                })

        speech_text = build_speech_text(detections)

        # inference_speed dict içinde ms değeri var
        speed_ms = int(result.speed.get("inference", 0))

        return {
            "objects":      detections,
            "speech_text":  speech_text,
            "frame_ms":     speed_ms,
        }

    # ── Yardımcı ──────────────────────────────────────────────────────────────

    @staticmethod
    def _resize(img: Image.Image, max_size: int) -> Image.Image:
        """
        En uzun kenarı max_size olacak şekilde oranı koruyarak küçültür.
        Zaten küçükse dokunmaz.
        """
        w, h = img.size
        if max(w, h) <= max_size:
            return img
        scale = max_size / max(w, h)
        new_w, new_h = int(w * scale), int(h * scale)
        return img.resize((new_w, new_h), Image.LANCZOS)


# Uygulama genelinde tek örnek (singleton)
detector = ObjectDetector()
