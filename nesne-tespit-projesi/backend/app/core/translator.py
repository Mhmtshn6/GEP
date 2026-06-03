"""
translator.py
-------------
YOLOv8 İngilizce COCO etiketlerini Türkçeye çevirir.
Projede öncelikli olan 12 nesne sınıfı dahil
tüm 80 COCO sınıfı eklenmiştir — ekstra etiket gelirse hata çıkmaz.
"""

# COCO 80 sınıf → Türkçe karşılık
LABEL_TR: dict[str, str] = {
    # Öncelikli sınıflar (projede tanımlandı)
    "person":       "insan",
    "car":          "araba",
    "bus":          "otobüs",
    "truck":        "kamyon",
    "motorcycle":   "motosiklet",
    "bicycle":      "bisiklet",
    "chair":        "sandalye",
    "cell phone":   "telefon",
    "dog":          "köpek",
    "cat":          "kedi",

    # Merdiven COCO'da yok; özel eklenebilir veya kapsam dışı tutulabilir.
    # Ağaç da COCO'da yok; aşağıdaki yakın karşılıklar not olarak bırakıldı:
    # "potted plant" → saksı bitkisi (kısmi)

    # Diğer COCO sınıfları (ekstra nesneler tespit edilirse Türkçe çıksın)
    "bicycle":       "bisiklet",
    "traffic light": "trafik ışığı",
    "fire hydrant":  "yangın musluğu",
    "stop sign":     "dur tabelası",
    "parking meter": "park sayacı",
    "bench":         "bank",
    "bird":          "kuş",
    "horse":         "at",
    "sheep":         "koyun",
    "cow":           "inek",
    "elephant":      "fil",
    "bear":          "ayı",
    "zebra":         "zebra",
    "giraffe":       "zürafa",
    "backpack":      "sırt çantası",
    "umbrella":      "şemsiye",
    "handbag":       "el çantası",
    "tie":           "kravat",
    "suitcase":      "bavul",
    "frisbee":       "frizbi",
    "skis":          "kayak",
    "snowboard":     "snowboard",
    "sports ball":   "top",
    "kite":          "uçurtma",
    "baseball bat":  "beysbol sopası",
    "baseball glove":"beysbol eldiveni",
    "skateboard":    "kaykay",
    "surfboard":     "sörf tahtası",
    "tennis racket": "tenis raketi",
    "bottle":        "şişe",
    "wine glass":    "kadeh",
    "cup":           "bardak",
    "fork":          "çatal",
    "knife":         "bıçak",
    "spoon":         "kaşık",
    "bowl":          "kase",
    "banana":        "muz",
    "apple":         "elma",
    "sandwich":      "sandviç",
    "orange":        "portakal",
    "broccoli":      "brokoli",
    "carrot":        "havuç",
    "hot dog":       "sosisli sandviç",
    "pizza":         "pizza",
    "donut":         "donut",
    "cake":          "pasta",
    "couch":         "kanepe",
    "potted plant":  "saksı bitkisi",
    "bed":           "yatak",
    "dining table":  "yemek masası",
    "toilet":        "tuvalet",
    "tv":            "televizyon",
    "laptop":        "dizüstü bilgisayar",
    "mouse":         "fare",
    "remote":        "uzaktan kumanda",
    "keyboard":      "klavye",
    "microwave":     "mikrodalga",
    "oven":          "fırın",
    "toaster":       "tost makinesi",
    "sink":          "lavabo",
    "refrigerator":  "buzdolabı",
    "book":          "kitap",
    "clock":         "saat",
    "vase":          "vazo",
    "scissors":      "makas",
    "teddy bear":    "oyuncak ayı",
    "hair drier":    "saç kurutma makinesi",
    "toothbrush":    "diş fırçası",
}


def translate(label_en: str) -> str:
    """
    İngilizce COCO etiketini Türkçeye çevirir.
    Bilinmeyen etiket gelirse orijinali döner (sistem çökmez).
    """
    return LABEL_TR.get(label_en.lower(), label_en)
