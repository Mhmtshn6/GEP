"""
main.py
-------
FastAPI uygulamasını oluşturur ve yapılandırır.

Lifespan pattern kullanılır:
  - Startup : YOLOv8 modeli yüklenir (warmup dahil)
  - Shutdown : Kaynaklar serbest bırakılır

Bu yaklaşım deprecated olan @app.on_event("startup") yerine
FastAPI'nin resmi önerisidir.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings
from app.core.detector import detector

# ── Logging yapılandırması ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Uygulama ömrü boyunca çalışacak başlatma / kapatma mantığı.
    yield'den önce: startup
    yield'den sonra: shutdown
    """
    # ── Startup ──────────────────────────────────────────────
    settings = get_settings()
    logger.info("=" * 50)
    logger.info("Nesne Tespit Sunucusu başlatılıyor...")
    logger.info(f"  Model  : {settings.model_path}")
    logger.info(f"  Conf   : {settings.confidence_threshold}")
    logger.info(f"  Port   : {settings.port}")
    logger.info("=" * 50)

    detector.load()  # Model yükle + warmup
    logger.info("Sunucu hazır. Bekleniyor...")

    yield  # Uygulama burada çalışır

    # ── Shutdown ──────────────────────────────────────────────
    logger.info("Sunucu kapatılıyor...")


# ── FastAPI uygulaması ────────────────────────────────────────────────────────

settings = get_settings()

app = FastAPI(
    title="Görme Engelliler İçin Nesne Tespit API",
    description=(
        "YOLOv8 tabanlı gerçek zamanlı nesne tespiti. "
        "Kamera görüntüsünden nesneleri tespit eder, "
        "konum ve mesafe bilgisiyle birlikte Türkçe sesli uyarı metni döner."
    ),
    version="1.0.0",
    docs_url="/docs",      # Swagger UI: http://localhost:8000/docs
    redoc_url="/redoc",    # ReDoc    : http://localhost:8000/redoc
    lifespan=lifespan,
)

# ── CORS middleware ───────────────────────────────────────────────────────────
# React Native localhost'tan farklı bir origin olduğu için CORS gereklidir.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Router ────────────────────────────────────────────────────────────────────
app.include_router(router)
