"""
postprocess.py
--------------
YOLOv8 ham çıktısını anlamlı bilgiye dönüştürür:
  - Bounding box'tan sol / orta / sağ konum analizi
  - Bounding box boyutuna dayalı kaba mesafe tahmini
  - Türkçe sesli uyarı metni üretimi

NOT: Tek kamerayla kesin mesafe ölçümü yapılamaz.
Bu modül, nesne boyutuna dayalı "kaba tahmin" üretir.
Tez yazarken bunu "boyut-tabanlı yaklaşık mesafe tahmini" olarak belirt.
"""

from dataclasses import dataclass


# ── Tip tanımları ──────────────────────────────────────────────────────────────

@dataclass
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float
    img_width: int
    img_height: int

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def area_ratio(self) -> float:
        """Nesnenin görüntü alanına oranı (0-1)."""
        img_area = self.img_width * self.img_height
        if img_area == 0:
            return 0.0
        return (self.width * self.height) / img_area

    @property
    def center_x(self) -> float:
        """Nesnenin yatay merkez koordinatı (normalize 0-1)."""
        return ((self.x1 + self.x2) / 2) / self.img_width


# ── Konum analizi ──────────────────────────────────────────────────────────────

# Görüntü 3 dikey şeride bölünür:
#   Sol  : 0.00 – 0.38
#   Orta : 0.38 – 0.62
#   Sağ  : 0.62 – 1.00
_LEFT_THRESHOLD  = 0.38
_RIGHT_THRESHOLD = 0.62


def get_position(bbox: BoundingBox) -> str:
    """
    Nesnenin yatay konumunu döner: 'sol' | 'orta' | 'sağ'
    """
    cx = bbox.center_x
    if cx < _LEFT_THRESHOLD:
        return "sol"
    elif cx > _RIGHT_THRESHOLD:
        return "sağ"
    else:
        return "orta"


# ── Kaba mesafe tahmini ────────────────────────────────────────────────────────

# Nesnenin görüntü alanını kapladığı orana göre yakınlık kademesi belirlenir.
# Eşik değerleri genel kullanım için ayarlanmıştır; nesneden nesneye farklılık gösterir.
_DISTANCE_THRESHOLDS = [
    (0.25, "çok yakın (~1m)"),
    (0.10, "yakın (~2-3m)"),
    (0.03, "orta mesafe (~5m)"),
    (0.01, "uzak (>5m)"),
]


def get_distance(bbox: BoundingBox) -> str:
    """
    Bounding box boyutuna göre kaba mesafe tahmini döner.
    Değer tamamen göreli; ışık ve perspektife bağlı hatalar olabilir.
    """
    ratio = bbox.area_ratio
    for threshold, label in _DISTANCE_THRESHOLDS:
        if ratio >= threshold:
            return label
    return "çok uzak"


# ── Sesli uyarı metni üretimi ──────────────────────────────────────────────────

def build_speech_text(detections: list[dict]) -> str:
    """
    Tespit edilen nesnelerden Türkçe sesli uyarı metni üretir.

    Öncelik sırası:
      1. Yakın nesneler önce söylenir.
      2. Aynı nesne birden fazla görünüyorsa sayıyla belirtilir.
      3. Maksimum 3 nesne bildirilir (kullanıcıyı bunaltmamak için).

    Örnek çıktı:
      "Solda çok yakın insan, ortada yakın araba"
    """
    if not detections:
        return ""

    # Mesafe önceliğine göre sırala (yakın → uzak)
    priority_order = ["çok yakın (~1m)", "yakın (~2-3m)", "orta mesafe (~5m)", "uzak (>5m)", "çok uzak"]
    sorted_dets = sorted(
        detections,
        key=lambda d: priority_order.index(d["distance"]) if d["distance"] in priority_order else 99
    )

    parts = []
    for det in sorted_dets[:3]:  # En fazla 3 nesne
        label    = det["label_tr"]
        position = det["position"]
        distance = det["distance"]
        parts.append(f"{position}da {distance} {label}")

    return ", ".join(parts)
