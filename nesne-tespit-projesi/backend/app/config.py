"""
config.py
---------
Tüm ortam değişkenleri tek yerden yönetilir.
Pydantic Settings .env dosyasını otomatik okur.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Sunucu
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # YOLOv8 modeli
    model_path: str = "app/models/yolov8s.pt"
    confidence_threshold: float = 0.50
    iou_threshold: float = 0.45

    # Görüntü ön işleme
    max_image_size: int = 640

    # CORS
    allowed_origins: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def origins_list(self) -> list[str]:
        """CORS origins'i virgülle ayrılmış string'den listeye çevirir."""
        if self.allowed_origins == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Ayarları bir kez yükle, sonra cache'ten sun.
    lru_cache sayesinde her request'te .env yeniden okunmaz.
    """
    return Settings()
