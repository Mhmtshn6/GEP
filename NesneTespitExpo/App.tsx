import React, { useEffect, useRef, useState } from "react";
import {
  View, Text, StyleSheet, TouchableOpacity,
  Alert, ActivityIndicator, SafeAreaView, StatusBar,
} from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as Speech from "expo-speech";
import { detectObjects, checkHealth, DetectionResponse } from "./src/services/api";
import { FRAME_INTERVAL_MS, JPEG_QUALITY, TTS_COOLDOWN_MS } from "./src/constants";

export default function App() {
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView>(null);

  const [isActive,    setIsActive]    = useState(false);
  const [serverReady, setServerReady] = useState(false);
  const [checking,    setChecking]    = useState(true);
  const [result,      setResult]      = useState<DetectionResponse | null>(null);
  const [error,       setError]       = useState<string | null>(null);
  const [muted,       setMuted]       = useState(false);
  const [fps,         setFps]         = useState(0);

  const isRunningRef  = useRef(false);
  const lastSpeech    = useRef({ text: "", time: 0 });
  const frameCountRef = useRef(0);

  // ── Başlatma ────────────────────────────────────────────────────────────────
  useEffect(() => {
    (async () => {
      if (!permission?.granted) {
        const res = await requestPermission();
        if (!res.granted) {
          Alert.alert("Kamera İzni", "Uygulama kamera iznine ihtiyaç duyuyor.");
          setChecking(false);
          return;
        }
      }
      const ready = await checkHealth();
      setServerReady(ready);
      if (!ready) {
        Alert.alert(
          "Sunucuya Ulaşılamıyor",
          "• Backend çalışıyor mu? (python run.py)\n• Telefon hotspot'a bağlı mı?\n• constants.ts'deki IP doğru mu?"
        );
      }
      setChecking(false);
    })();
  }, []);

  // ── FPS sayacı ──────────────────────────────────────────────────────────────
  useEffect(() => {
    const t = setInterval(() => { setFps(frameCountRef.current); frameCountRef.current = 0; }, 1000);
    return () => clearInterval(t);
  }, []);

  // ── Tespit döngüsü ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!isActive || !serverReady) return;
    const interval = setInterval(async () => {
      if (isRunningRef.current || !cameraRef.current) return;
      isRunningRef.current = true;
      try {
        const photo = await cameraRef.current.takePictureAsync({
  quality: JPEG_QUALITY,
  base64: true,
  skipProcessing: true,
  shutterSound: false,
  exif: false,
});
        if (!photo?.base64) return;

        const data = await detectObjects(photo.base64);
        setResult(data);
        setError(null);
        frameCountRef.current += 1;

        if (data.speech_text && !muted) {
          const now = Date.now();
          const dup = data.speech_text === lastSpeech.current.text && now - lastSpeech.current.time < TTS_COOLDOWN_MS;
          if (!dup) {
            Speech.stop();
            Speech.speak(data.speech_text, { language: "tr-TR", rate: 0.9 });
            lastSpeech.current = { text: data.speech_text, time: now };
          }
        }
      } catch {
        setError("Sunucuya ulaşılamıyor");
      } finally {
        isRunningRef.current = false;
      }
    }, FRAME_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [isActive, serverReady, muted]);

  if (checking) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#FFF" />
        <Text style={styles.loadingText}>Sunucu kontrol ediliyor...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="transparent" translucent />

      <CameraView ref={cameraRef} style={StyleSheet.absoluteFill} facing="back"   animateShutter={false} />

      {/* Üst bilgi */}
      <SafeAreaView style={styles.topBar}>
        <View style={styles.topBarInner}>
          <Text style={styles.statusText}>{isActive ? "Analiz ediliyor" : "Beklemede"}</Text>
          <View style={styles.row}>
            {result && <Text style={styles.statsText}>{result.total_ms}ms  {fps}fps</Text>}
            <View style={[styles.dot, serverReady ? styles.dotGreen : styles.dotRed]} />
          </View>
        </View>
      </SafeAreaView>

      {/* Hata */}
      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Tespitler */}
      {result && result.objects.length > 0 && (
        <View style={styles.detectionList}>
          {result.objects.slice(0, 4).map((obj, i) => (
            <View key={i} style={styles.detectionItem}>
              <View style={[styles.posDot, posColor(obj.position)]} />
              <Text style={styles.detectionText}>
                {obj.label_tr}
                <Text style={styles.detectionSub}>{"  "}{obj.position}  {obj.distance}  %{Math.round(obj.confidence * 100)}</Text>
              </Text>
            </View>
          ))}
        </View>
      )}

      {/* TTS metni */}
      {!!result?.speech_text && (
        <View style={styles.speechBubble}>
          <Text style={styles.speechText}>{result.speech_text}</Text>
        </View>
      )}

      {/* Alt kontroller */}
      <SafeAreaView style={styles.bottomBar}>
        <TouchableOpacity style={styles.iconBtn} onPress={() => { setMuted(m => !m); Speech.stop(); }}>
          <Text style={styles.iconText}>{muted ? "🔇" : "🔊"}</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.mainBtn, isActive && styles.mainBtnActive]}
          onPress={() => setIsActive(a => !a)}
          disabled={!serverReady}
        >
          <Text style={styles.mainBtnText}>{isActive ? "Durdur" : "Başlat"}</Text>
        </TouchableOpacity>
        <View style={styles.iconBtn} />
      </SafeAreaView>
    </View>
  );
}

function posColor(pos: string) {
  if (pos === "sol") return { backgroundColor: "#FF6B6B" };
  if (pos === "sağ") return { backgroundColor: "#74B9FF" };
  return { backgroundColor: "#55EFC4" };
}

const styles = StyleSheet.create({
  container:     { flex: 1, backgroundColor: "#000" },
  center:        { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#111", gap: 16 },
  loadingText:   { color: "#FFF", fontSize: 16 },
  topBar:        { position: "absolute", top: 0, left: 0, right: 0 },
  topBarInner:   { flexDirection: "row", justifyContent: "space-between", alignItems: "center",
                   backgroundColor: "rgba(0,0,0,0.5)", marginHorizontal: 12, marginTop: 8,
                   borderRadius: 10, paddingHorizontal: 14, paddingVertical: 8 },
  statusText:    { color: "#FFF", fontSize: 13, fontWeight: "500" },
  row:           { flexDirection: "row", alignItems: "center", gap: 10 },
  statsText:     { color: "rgba(255,255,255,0.7)", fontSize: 12 },
  dot:           { width: 10, height: 10, borderRadius: 5 },
  dotGreen:      { backgroundColor: "#55EFC4" },
  dotRed:        { backgroundColor: "#FF6B6B" },
  errorBanner:   { position: "absolute", top: 80, alignSelf: "center",
                   backgroundColor: "rgba(220,53,69,0.85)", borderRadius: 8, padding: 10 },
  errorText:     { color: "#FFF", fontSize: 13 },
  detectionList: { position: "absolute", bottom: 140, left: 12, gap: 6 },
  detectionItem: { flexDirection: "row", alignItems: "center", backgroundColor: "rgba(0,0,0,0.6)",
                   borderRadius: 8, paddingHorizontal: 10, paddingVertical: 7, alignSelf: "flex-start" },
  posDot:        { width: 10, height: 10, borderRadius: 5, marginRight: 8 },
  detectionText: { color: "#FFF", fontSize: 14, fontWeight: "500" },
  detectionSub:  { color: "rgba(255,255,255,0.65)", fontSize: 12, fontWeight: "400" },
  speechBubble:  { position: "absolute", bottom: 110, alignSelf: "center",
                   backgroundColor: "rgba(0,0,0,0.75)", borderRadius: 10, paddingHorizontal: 16, paddingVertical: 10 },
  speechText:    { color: "#FFF", fontSize: 15, textAlign: "center", fontWeight: "500" },
  bottomBar:     { position: "absolute", bottom: 0, left: 0, right: 0, flexDirection: "row",
                   justifyContent: "space-between", alignItems: "center",
                   paddingHorizontal: 24, paddingBottom: 28, paddingTop: 12,
                   backgroundColor: "rgba(0,0,0,0.6)" },
  iconBtn:       { width: 48, height: 48, justifyContent: "center", alignItems: "center" },
  iconText:      { fontSize: 24 },
  mainBtn:       { paddingHorizontal: 40, paddingVertical: 14, borderRadius: 28, backgroundColor: "#FFF" },
  mainBtnActive: { backgroundColor: "#FF6B6B" },
  mainBtnText:   { fontSize: 16, fontWeight: "600", color: "#111" },
});
