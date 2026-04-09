code = '''import React, { useState, useRef, useEffect } from "react";
import { View, Text, StyleSheet, TouchableOpacity, FlatList, StatusBar, Dimensions, ScrollView, TextInput, Modal, ImageBackground, Platform } from "react-native";
import { Video, ResizeMode } from "expo-av";
import * as DocumentPicker from "expo-document-picker";
import * as MediaLibrary from "expo-media-library";
import AsyncStorage from "@react-native-async-storage/async-storage";

const { width: W, height: H } = Dimensions.get("window");
const SPEEDS = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0];
const ACCENT = "#FF6B00";
const BG = "#0a0a0a";
const CARD = "#161616";
const SURFACE = "#1f1f1f";

export default function App() {
  const [tab, setTab] = useState("videos");
  const [screen, setScreen] = useState("home");
  const [videos, setVideos] = useState([]);
  const [current, setCurrent] = useState(null);
  const [playing, setPlaying] = useState(false);
  const [pos, setPos] = useState(0);
  const [dur, setDur] = useState(0);
  const [speed, setSpeed] = useState(1.0);
  const [loop, setLoop] = useState(false);
  const [showCtrl, setShowCtrl] = useState(true);
  const [showSpeed, setShowSpeed] = useState(false);
  const [history, setHistory] = useState([]);
  const [netUrl, setNetUrl] = useState("");
  const [idx, setIdx] = useState(0);
  const [locked, setLocked] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const videoRef = useRef(null);
  const ctrlTimer = useRef(null);useEffect(() => {
    AsyncStorage.getItem("history").then(h => { if (h) setHistory(JSON.parse(h)); });
    MediaLibrary.requestPermissionsAsync();
  }, []);

  const fmt = ms => {
    const s = Math.floor(ms / 1000), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
    return h > 0 ? h + ":" + String(m).padStart(2, "0") + ":" + String(sec).padStart(2, "0") : m + ":" + String(sec).padStart(2, "0");
  };

  const resetTimer = () => {
    if (ctrlTimer.current) clearTimeout(ctrlTimer.current);
    setShowCtrl(true);
    ctrlTimer.current = setTimeout(() => setShowCtrl(false), 4000);
  };

  const play = async (v, i) => {
    setCurrent(v); setIdx(i || 0); setScreen("player"); setPlaying(true); setShowCtrl(true);
    const h = [v, ...history.filter(x => x.id !== v.id)].slice(0, 50);
    setHistory(h); AsyncStorage.setItem("history", JSON.stringify(h));
  };

  const pickVideo = async () => {
    try {
      const r = await DocumentPicker.getDocumentAsync({ type: "video/*", multiple: true });
      if (!r.canceled && r.assets) setVideos(p => [...p, ...r.assets.map(a => ({ id: Date.now() + Math.random(), uri: a.uri, name: a.name || "Video" }))]);
    } catch (e) {}
  };

  const loadGallery = async () => {
    try {
      const { assets } = await MediaLibrary.getAssetsAsync({ mediaType: "video", first: 200 });
      setVideos(p => { const ids = new Set(p.map(v => v.id)); return [...p, ...assets.filter(a => !ids.has(a.id)).map(a => ({ id: a.id, uri: a.uri, name: a.filename, duration: a.duration }))]; });
    } catch (e) {}
  };

  const onStatus = s => {
    if (s.isLoaded) {
      setPos(s.positionMillis || 0); setDur(s.durationMillis || 0); setPlaying(s.isPlaying);
      if (s.didJustFinish) { if (loop) { videoRef.current?.replayAsync(); } else if (idx < videos.length - 1) { play(videos[idx + 1], idx + 1); } }
    }
  };

  const pct = dur > 0 ? (pos / dur) * 100 : 0;

  if (screen === "player" && current) return (
    <View style={{ flex: 1, backgroundColor: "#000" }}>
      <StatusBar hidden />
      <TouchableOpacity activeOpacity={1} style={{ flex: 1 }} onPress={() => { if (!locked) resetTimer(); }}>
        <Video ref={videoRef} source={{ uri: current.uri }} style={{ flex: 1 }} resizeMode={fullscreen ? ResizeMode.COVER : ResizeMode.CONTAIN} shouldPlay={playing} rate={speed} isLooping={loop} onPlaybackStatusUpdate={onStatus} />
      </TouchableOpacity>{showCtrl && !locked && (
        <View style={p.overlay}>
          {/* Top gradient bar */}
          <View style={p.topGrad}>
            <TouchableOpacity onPress={() => { setScreen("home"); setPlaying(false); }} style={p.backBtn}>
              <Text style={p.backIco}>‹</Text>
            </TouchableOpacity>
            <View style={{ flex: 1 }}>
              <Text style={p.vidTitle} numberOfLines={1}>{current.name}</Text>
              <Text style={p.vidSub}>{fmt(pos)} / {fmt(dur)}</Text>
            </View>
            <TouchableOpacity onPress={() => setFullscreen(f => !f)} style={p.iconBtn}>
              <Text style={p.iconTxt}>{fullscreen ? "⊡" : "⛶"}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => setLocked(true)} style={p.iconBtn}>
              <Text style={p.iconTxt}>🔒</Text>
            </TouchableOpacity>
          </View>

          {/* Center controls */}
          <View style={p.centerRow}>
            <TouchableOpacity onPress={() => { if (idx > 0) play(videos[idx - 1], idx - 1); }} style={p.ctrlBtn}>
              <Text style={p.ctrlIco}>⏮</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => videoRef.current?.setPositionAsync(Math.max(0, pos - 10000))} style={p.ctrlBtn}>
              <Text style={p.ctrlIco}>⏪</Text>
              <Text style={p.ctrlLbl}>10s</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => { playing ? videoRef.current?.pauseAsync() : videoRef.current?.playAsync(); setPlaying(!playing); }} style={p.playBtn}>
              <Text style={p.playIco}>{playing ? "⏸" : "▶"}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => videoRef.current?.setPositionAsync(Math.min(dur, pos + 10000))} style={p.ctrlBtn}>
              <Text style={p.ctrlIco}>⏩</Text>
              <Text style={p.ctrlLbl}>10s</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => { if (idx < videos.length - 1) play(videos[idx + 1], idx + 1); }} style={p.ctrlBtn}>
              <Text style={p.ctrlIco}>⏭</Text>
            </TouchableOpacity>
          </View>
return (
    <View style={{ flex: 1, backgroundColor: BG }}>
      <StatusBar barStyle="light-content" backgroundColor={BG} />

      {/* Header */}
      <View style={h.header}>
        <View>
          <Text style={h.appName}>NexPlayer</Text>
          <Text style={h.appSub}>Pro Edition ⚡</Text>
        </View>
        <TouchableOpacity onPress={loadGallery} style={h.headerBtn}>
          <Text style={{ color: "#fff", fontSize: 13, fontWeight: "700" }}>+ Gallery</Text>
        </TouchableOpacity>
      </View>

      {/* Tab bar */}
      <View style={h.tabs}>
        {[["videos", "🎬 Videos"], ["history", "🕐 History"], ["network", "🌐 Stream"]].map(([t, l]) => (
          <TouchableOpacity key={t} style={[h.tab, tab === t && h.tabActive]} onPress={() => setTab(t)}>
            <Text style={[h.tabTxt, tab === t && h.tabTxtActive]}>{l}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Videos tab */}
      {tab === "videos" && (
        <>
          <View style={h.actionRow}>
            <TouchableOpacity style={h.addBtn} onPress={pickVideo}>
              <Text style={h.addBtnTxt}>＋ Add Video</Text>
            </TouchableOpacity>
            <TouchableOpacity style={h.clearBtn} onPress={() => setVideos([])}>
              <Text style={{ color: "#ff4444", fontSize: 13 }}>🗑 Clear</Text>
            </TouchableOpacity>
          </View>
          {videos.length === 0 ? (
            <View style={h.empty}>
              <Text style={{ fontSize: 72 }}>🎬</Text>
              <Text style={h.emptyTitle}>No Videos Yet</Text>
              <Text style={h.emptySub}>Tap "+ Add Video" or "+ Gallery"</Text>
              <TouchableOpacity style={h.emptyBtn} onPress={pickVideo}>
                <Text style={{ color: "#fff", fontWeight: "700" }}>＋ Add Video</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <FlatList
              data={videos}
              keyExtractor={x => String(x.id)}
              contentContainerStyle={{ padding: 16, gap: 10 }}
              renderItem={({ item, index }) => (
                <TouchableOpacity style={h.videoCard} onPress={() => play(item, index)}>
                  <View style={h.thumb}>
                    <Text style={{ fontSize: 32 }}>🎥</Text>
                    {item.duration ? <View style={h.durBadge}><Text style={h.durTxt}>{fmt(item.duration * 1000)}</Text></View> : null}
                  </View>
                  <View style={{ flex: 1, gap: 4 }}>
                    <Text style={h.videoName} numberOfLines={2}>{item.name}</Text>
                    <Text style={h.videoMeta}>Tap to play</Text>
                  </View>
                  <View style={{ gap: 8 }}>
                    <TouchableOpacity onPress={() => play(item, index)} style={h.playSmall}>
                      <Text style={{ color: "#fff", fontSize: 14 }}>▶</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => setVideos(p => p.filter(v => v.id !== item.id))}>
                      <Text style={{ color: "#ff4444", fontSize: 18 }}>✕</Text>
                    </TouchableOpacity>
                  </View>
                </TouchableOpacity>
              )}
            />
          )}
        </>
      )}

      {/* History tab */}
      {tab === "history" && (
        <View style={{ flex: 1 }}>
          <View style={h.actionRow}>
            <Text style={{ color: "#888", fontSize: 13 }}>{history.length} videos watched</Text>
            <TouchableOpacity onPress={() => { setHistory([]); AsyncStorage.removeItem("history"); }}>
              <Text style={{ color: "#ff4444", fontSize: 13 }}>Clear All</Text>
            </TouchableOpacity>
          </View>
          {history.length === 0 ? (
            <View style={h.empty}>
              <Text style={{ fontSize: 64 }}>🕐</Text>
              <Text style={h.emptyTitle}>No History</Text>
              <Text style={h.emptySub}>Videos you watch will appear here</Text>
            </View>
          ) : (
            <FlatList data={history} keyExtractor={(x, i) => x.id + i} contentContainerStyle={{ padding: 16, gap: 10 }}
              renderItem={({ item, index }) => (
                <TouchableOpacity style={h.videoCard} onPress={() => play(item, index)}>
                  <View style={h.thumb}><Text style={{ fontSize: 32 }}>🎥</Text></View>
                  <View style={{ flex: 1 }}>
                    <Text style={h.videoName} numberOfLines={2}>{item.name}</Text>
                    <Text style={h.videoMeta}>Recently watched</Text>
                  </View>
                  <Text style={{ color: ACCENT, fontSize: 22 }}>▶</Text>
                </TouchableOpacity>
              )}
            />
          )}
        </View>
      )}

      {/* Network tab */}
      {tab === "network" && (
        <View style={{ flex: 1, padding: 20 }}>
          <Text style={h.networkTitle}>Stream Online Video</Text>
          <Text style={h.networkSub}>Enter any video URL or stream link</Text>
          <TextInput
            style={h.urlInput}
            placeholder="https://example.com/video.mp4"
            placeholderTextColor="#444"
            value={netUrl}
            onChangeText={setNetUrl}
            autoCapitalize="none"
            multiline
          />
          <TouchableOpacity style={h.streamBtn} onPress={() => { if (netUrl.trim()) play({ id: "net" + Date.now(), uri: netUrl.trim(), name: "Network Stream" }, 0); }}>
            <Text style={h.streamBtnTxt}>▶ Play Stream</Text>
          </TouchableOpacity>
          <View style={h.supportBox}>
            <Text style={h.supportTitle}>Supported Formats</Text>
            <Text style={h.supportTxt}>MP4 • MKV • M3U8 • HLS • RTSP • WebM</Text>
          </View>
        </View>
      )}
    </View>
  );
}const p = StyleSheet.create({
  overlay: { ...StyleSheet.absoluteFillObject, justifyContent: "space-between" },
  topGrad: { flexDirection: "row", alignItems: "center", paddingTop: 48, paddingHorizontal: 12, paddingBottom: 16, backgroundColor: "rgba(0,0,0,0.7)", gap: 8 },
  backBtn: { width: 40, height: 40, justifyContent: "center", alignItems: "center" },
  backIco: { color: "#fff", fontSize: 36, fontWeight: "300", marginTop: -4 },
  vidTitle: { color: "#fff", fontSize: 14, fontWeight: "700" },
  vidSub: { color: "rgba(255,255,255,0.6)", fontSize: 11, marginTop: 2 },
  iconBtn: { width: 40, height: 40, justifyContent: "center", alignItems: "center" },
  iconTxt: { fontSize: 20 },
  centerRow: { flexDirection: "row", justifyContent: "center", alignItems: "center", gap: 16 },
  ctrlBtn: { alignItems: "center", width: 60, height: 60, justifyContent: "center" },
  ctrlIco: { fontSize: 28, color: "#fff" },
  ctrlLbl: { color: "rgba(255,255,255,0.6)", fontSize: 10, marginTop: 2 },
  playBtn: { width: 72, height: 72, borderRadius: 36, backgroundColor: "#FF6B00", justifyContent: "center", alignItems: "center", shadowColor: "#FF6B00", shadowOpacity: 0.5, shadowRadius: 20, elevation: 10 },
  playIco: { fontSize: 32, color: "#fff" },
  botGrad: { backgroundColor: "rgba(0,0,0,0.7)", paddingBottom: 32, paddingTop: 12, paddingHorizontal: 16 },
  progRow: { flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 16 },
  timeLeft: { color: "#fff", fontSize: 11, width: 36 },
  timeRight: { color: "#fff", fontSize: 11, width: 36, textAlign: "right" },
  progTrack: { flex: 1, height: 20, justifyContent: "center" },
  progBg: { height: 3, backgroundColor: "rgba(255,255,255,0.2)", borderRadius: 2, position: "relative" },
  progFill: { height: 3, backgroundColor: "#FF6B00", borderRadius: 2 },
  progDot: { position: "absolute", top: -5, width: 14, height: 14, borderRadius: 7, backgroundColor: "#FF6B00", marginLeft: -7 },
  botBtns: { flexDirection: "row", gap: 10 },
  botChip: { backgroundColor: "rgba(255,255,255,0.15)", paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, borderWidth: 1, borderColor: "rgba(255,255,255,0.1)" },
  botChipTxt: { color: "#fff", fontSize: 12, fontWeight: "700" },
  lockScreen: { ...StyleSheet.absoluteFillObject, backgroundColor: "rgba(0,0,0,0.85)", justifyContent: "center", alignItems: "center" },
  lockBox: { alignItems: "center" },
  modalBg: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "flex-end" },
  speedSheet: { backgroundColor: "#1a1a1a", borderTopLeftRadius: 24, borderTopRightRadius: 24, paddingBottom: 40 },
  sheetHandle: { width: 40, height: 4, backgroundColor: "#333", borderRadius: 2, alignSelf: "center", marginTop: 12, marginBottom: 8 },
  sheetTitle: { color: "#fff", fontSize: 16, fontWeight: "800", padding: 16, paddingBottom: 8 },
  speedRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: 16, borderTopWidth: 0.5, borderColor: "#2a2a2a" },
  speedActive: { backgroundColor: "rgba(255,107,0,0.1)" },
  speedTxt: { color: "#fff", fontSize: 15 },
});const h = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: 20, paddingTop: 52, paddingBottom: 16, backgroundColor: "#111" },
  appName: { color: "#fff", fontSize: 26, fontWeight: "900", letterSpacing: -0.5 },
  appSub: { color: "#FF6B00", fontSize: 12, fontWeight: "700", marginTop: 1 },
  headerBtn: { backgroundColor: "#FF6B00", paddingHorizontal: 16, paddingVertical: 10, borderRadius: 20 },
  tabs: { flexDirection: "row", backgroundColor: "#111", paddingHorizontal: 16, paddingBottom: 12, gap: 8 },
  tab: { flex: 1, paddingVertical: 10, borderRadius: 12, alignItems: "center", backgroundColor: "#1a1a1a" },
  tabActive: { backgroundColor: "#FF6B00" },
  tabTxt: { color: "#666", fontSize: 12, fontWeight: "700" },
  tabTxtActive: { color: "#fff" },
  actionRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: 16, paddingVertical: 12 },
  addBtn: { backgroundColor: "#FF6B00", paddingHorizontal: 20, paddingVertical: 10, borderRadius: 20 },
  addBtnTxt: { color: "#fff", fontWeight: "800", fontSize: 14 },
  clearBtn: { paddingHorizontal: 12, paddingVertical: 10 },
  empty: { flex: 1, justifyContent: "center", alignItems: "center", gap: 12, paddingBottom: 80 },
  emptyTitle: { color: "#fff", fontSize: 20, fontWeight: "800" },
  emptySub: { color: "#555", fontSize: 14 },
  emptyBtn: { backgroundColor: "#FF6B00", paddingHorizontal: 24, paddingVertical: 12, borderRadius: 24, marginTop: 8 },
  videoCard: { flexDirection: "row", alignItems: "center", backgroundColor: "#161616", borderRadius: 16, padding: 12, gap: 12 },
  thumb: { width: 80, height: 56, backgroundColor: "#0a0a0a", borderRadius: 10, justifyContent: "center", alignItems: "center", position: "relative" },
  durBadge: { position: "absolute", bottom: 4, right: 4, backgroundColor: "rgba(0,0,0,0.8)", paddingHorizontal: 4, paddingVertical: 2, borderRadius: 4 },
  durTxt: { color: "#fff", fontSize: 10, fontWeight: "700" },
  videoName: { color: "#fff", fontSize: 14, fontWeight: "700" },
  videoMeta: { color: "#555", fontSize: 12 },
  playSmall: { backgroundColor: "#FF6B00", width: 32, height: 32, borderRadius: 16, justifyContent: "center", alignItems: "center" },
  networkTitle: { color: "#fff", fontSize: 22, fontWeight: "800", marginBottom: 4 },
  networkSub: { color: "#555", fontSize: 14, marginBottom: 20 },
  urlInput: { backgroundColor: "#161616", color: "#fff", borderRadius: 16, padding: 16, fontSize: 14, borderWidth: 1, borderColor: "#2a2a2a", minHeight: 80, marginBottom: 16 },
  streamBtn: { backgroundColor: "#FF6B00", padding: 18, borderRadius: 16, alignItems: "center", marginBottom: 24 },
  streamBtnTxt: { color: "#fff", fontSize: 16, fontWeight: "800" },
  supportBox: { backgroundColor: "#161616", borderRadius: 16, padding: 16 },
  supportTitle: { color: "#888", fontSize: 12, fontWeight: "700", marginBottom: 6 },
  supportTxt: { color: "#555", fontSize: 13 },
});
'''
f = open("App.tsx", "w")
f.write(code)
f.close()
print("Done! Ultra Pro UI written.")
