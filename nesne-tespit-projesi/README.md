# Görme Engelliler İçin Derin Öğrenme Tabanlı Gerçek Zamanlı Nesne Tespit Sistemi

YOLOv8 + FastAPI (Python) + React Native tabanlı mobil nesne tespit ve Türkçe sesli yönlendirme sistemi.

---

## Proje Yapısı

```
nesne-tespit-projesi/
├── backend/          # Python FastAPI sunucusu
└── mobile/           # React Native uygulaması
```

---

## Backend Kurulumu

```bash
cd backend

# 1. Sanal ortam oluştur ve aktifleştir
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. .env dosyasını oluştur
cp .env.example .env

# 4. YOLOv8 modelini indir (otomatik indirilir)
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
mv yolov8n.pt app/models/

# 5. Sunucuyu başlat
python run.py
# → http://localhost:8000/docs adresinde Swagger UI açılır
```

---

## Mobile Kurulumu

```bash
cd mobile

# 1. Node bağımlılıklarını yükle
npm install

# 2. iOS için (yalnızca macOS)
cd ios && pod install && cd ..

# 3. constants.ts dosyasında API_BASE_URL'i güncelle
#    Bilgisayarın yerel IP'sini yaz (ipconfig / ifconfig)

# 4. Uygulamayı çalıştır
npx react-native run-android   # Android
npx react-native run-ios       # iOS
```

---

## Android Ek Ayarlar

`android/app/src/main/AndroidManifest.xml` içine şu satırı ekle:

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.INTERNET" />

<!-- HTTP (yerel geliştirme) için -->
<application android:usesCleartextTraffic="true" ...>
```

## iOS Ek Ayarlar

`ios/NesneTespit/Info.plist` içine şu anahtarı ekle:

```xml
<key>NSCameraUsageDescription</key>
<string>Nesne tespiti için kamera erişimi gereklidir.</string>
```

---

## API Dokümantasyonu

Sunucu çalışırken: **http://localhost:8000/docs**

### POST /detect

Görüntüdeki nesneleri tespit eder.

**Request:** `multipart/form-data` — `image` alanında JPEG/PNG

**Response:**
```json
{
  "objects": [
    {
      "label_en":   "person",
      "label_tr":   "insan",
      "confidence": 0.92,
      "position":   "sol",
      "distance":   "yakın (~2-3m)",
      "bbox": { "x1": 45, "y1": 10, "x2": 180, "y2": 380 }
    }
  ],
  "speech_text": "solda yakın (~2-3m) insan",
  "frame_ms":    38,
  "total_ms":    52
}
```

---

## Olası Hatalar

| Hata | Çözüm |
|------|-------|
| `ModuleNotFoundError: ultralytics` | `source venv/bin/activate` ile ortamı aktifleştir |
| `Network request failed` (Android) | `AndroidManifest.xml`'e `usesCleartextTraffic="true"` ekle |
| TTS Türkçe çalışmıyor | Telefon Ayarlar → Erişilebilirlik → Metin Okuma → Türkçe dili indir |
| `CUDA out of memory` | `detector.py`'de `model.to("cpu")` ekle |
| `422 Unprocessable Entity` | Form field adının `image` olduğunu kontrol et |
