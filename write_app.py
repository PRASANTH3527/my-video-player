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
  const ctrlTimer = useRef(null);

  useEffect(() => {
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
cat >> write_app.py << 'PYEOF'

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
      </TouchableOpacity>
cat >> write_app.py << 'PYEOF'

      {showCtrl && !locked && (
        <View style={p.overlay}>
          <View style={p.topGrad}>
            <TouchableOpacity onPress={() => { setScreen("home"); setPlaying(false); }} style={p.backBtn}>
              <Text style={p.backIco}>‹</Text>
            </TouchableOpacity>
            <View style={{ flex: 1 }}>
              <Text style={p.vidTitle} numberOfLines={1}>{current.name}</Text>
              <Text style={p.vidSub}>{fmt(pos)} / {fmt(dur)}</Text>
            </View>
          </View>
        </View>
      )}
    </View>
  );

  return (
    <View style={{ flex: 1, backgroundColor: BG }}>
      <StatusBar barStyle="light-content" backgroundColor={BG} />
      <TouchableOpacity onPress={pickVideo}>
        <Text style={{ color: "#fff", margin: 20 }}>＋ Add Video</Text>
      </TouchableOpacity>
      <FlatList data={videos} keyExtractor={x => String(x.id)} renderItem={({ item, index }) => (
        <TouchableOpacity onPress={() => play(item, index)}>
          <Text style={{ color: "#fff", padding: 10 }}>{item.name}</Text>
        </TouchableOpacity>
      )}/>
    </View>
  );
}

const p = StyleSheet.create({
  overlay: { ...StyleSheet.absoluteFillObject, justifyContent: "space-between" },
  topGrad: { flexDirection: "row", alignItems: "center", paddingTop: 48, paddingHorizontal: 12, paddingBottom: 16, backgroundColor: "rgba(0,0,0,0.7)" },
  backBtn: { width: 40, height: 40, justifyContent: "center", alignItems: "center" },
  backIco: { color: "#fff", fontSize: 36 }
});
'''
f = open("App.tsx", "w")
f.write(code)
f.close()
print("🔥 FULL Ultra Pro UI Ready!")
