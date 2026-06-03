"""
run.py
------
Geliştirme ortamında sunucuyu başlatır.
Kullanım: python run.py
"""

import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,   # debug=True iken kod değişikliklerinde otomatik yeniden başlar
        log_level="debug" if settings.debug else "info",
    )
