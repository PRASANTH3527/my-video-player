code = '''import React, { useState, useRef, useEffect } from "react";
import { View, Text, StyleSheet, TouchableOpacity, FlatList, StatusBar, Dimensions, ScrollView, TextInput, Modal } from "react-native";
import { Video, ResizeMode } from "expo-av";
import * as DocumentPicker from "expo-document-picker";
import * as MediaLibrary from "expo-media-library";
import AsyncStorage from "@react-native-async-storage/async-storage";

const { width: W } = Dimensions.get("window");
const SPEEDS = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0];

export default function App() {
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
  const videoRef = useRef(null);

  useEffect(() => {
    AsyncStorage.getItem("history").then(h => { if (h) setHistory(JSON.parse(h)); });
    MediaLibrary.requestPermissionsAsync();
  }, []);

  const fmt = ms => {
    const s = Math.floor(ms / 1000);
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return m + ":" + String(sec).padStart(2, "0");
  };

  const play = async (v, i) => {
    setCurrent(v);
    setIdx(i || 0);
    setScreen("player");
    setPlaying(true);
    setShowCtrl(true);
    const h = [v, ...history.filter(x => x.id !== v.id)].slice(0, 30);
    setHistory(h);
    AsyncStorage.setItem("history", JSON.stringify(h));
  };

  const pickVideo = async () => {
    try {
      const r = await DocumentPicker.getDocumentAsync({ type: "video/*", multiple: true });
      if (!r.canceled && r.assets) {
        setVideos(p => [...p, ...r.assets.map(a => ({ id: Date.now() + Math.random(), uri: a.uri, name: a.name || "Video" }))]);
      }
    } catch (e) {}
  };

  const loadGallery = async () => {
    try {
      const { assets } = await MediaLibrary.getAssetsAsync({ mediaType: "video", first: 200 });
      setVideos(p => {
        const ids = new Set(p.map(v => v.id));
        return [...p, ...assets.filter(a => !ids.has(a.id)).map(a => ({ id: a.id, uri: a.uri, name: a.filename, duration: a.duration }))];
      });
    } catch (e) {}
  };

  const onStatus = s => {
    if (s.isLoaded) {
      setPos(s.positionMillis || 0);
      setDur(s.durationMillis || 0);
      setPlaying(s.isPlaying);
      if (s.didJustFinish) {
        if (loop) {
          videoRef.current?.replayAsync();
        } else if (idx < videos.length - 1) {
          play(videos[idx + 1], idx + 1);
        }
      }
    }
  };

  if (screen === "player" && current) return (
    <View style={{ flex: 1, backgroundColor: "#000" }}>
      <StatusBar hidden />
      <TouchableOpacity activeOpacity={1} style={{ flex: 1 }} onPress={() => setShowCtrl(p => !p)}>
        <Video
          ref={videoRef}
          source={{ uri: current.uri }}
          style={{ flex: 1 }}
          resizeMode={ResizeMode.CONTAIN}
          shouldPlay={playing}
          rate={speed}
          isLooping={loop}
          onPlaybackStatusUpdate={onStatus}
        />
      </TouchableOpacity>
      {showCtrl && (
        <View style={s.overlay}>
          <View style={s.topBar}>
            <TouchableOpacity onPress={() => { setScreen("home"); setPlaying(false); }}>
              <Text style={s.back}>← Back</Text>
            </TouchableOpacity>
            <Text style={s.title} numberOfLines={1}>{current.name}</Text>
          </View>
          <View style={s.center}>
            <TouchableOpacity onPress={() => { if (idx > 0) play(videos[idx - 1], idx - 1); }}>
              <Text style={s.btn}>⏮</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => videoRef.current?.setPositionAsync(Math.max(0, pos - 10000))}>
              <Text style={s.btn}>⏪</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => { playing ? videoRef.current?.pauseAsync() : videoRef.current?.playAsync(); setPlaying(!playing); }}>
              <Text style={[s.btn, { fontSize: 56, color: "#FF6B00" }]}>{playing ? "⏸" : "▶"}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => videoRef.current?.setPositionAsync(Math.min(dur, pos + 10000))}>
              <Text style={s.btn}>⏩</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => { if (idx < videos.length - 1) play(videos[idx + 1], idx + 1); }}>
              <Text style={s.btn}>⏭</Text>
            </TouchableOpacity>
          </View>
          <View style={s.prog}>
            <Text style={s.time}>{fmt(pos)}</Text>
            <TouchableOpacity style={{ flex: 1, height: 24, justifyContent: "center" }} onPress={e => videoRef.current?.setPositionAsync((e.nativeEvent.locationX / (W - 120)) * dur)}>
              <View style={{ height: 4, backgroundColor: "rgba(255,255,255,0.3)", borderRadius: 2 }}>
                <View style={{ height: 4, backgroundColor: "#FF6B00", borderRadius: 2, width: dur > 0 ? ((pos / dur) * 100) + "%" : "0%" }} />
              </View>
            </TouchableOpacity>
            <Text style={s.time}>{fmt(dur)}</Text>
          </View>
          <View style={s.bot}>
            <TouchableOpacity onPress={() => setShowSpeed(true)} style={s.botBtn}>
              <Text style={s.botTxt}>{speed}x Speed</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => setLoop(!loop)} style={s.botBtn}>
              <Text style={s.botTxt}>{loop ? "🔂 Loop" : "🔁 Loop"}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={pickVideo} style={s.botBtn}>
              <Text style={s.botTxt}>+ Video</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
      <Modal visible={showSpeed} transparent animationType="fade">
        <TouchableOpacity style={s.modalBg} onPress={() => setShowSpeed(false)}>
          <View style={{ backgroundColor: "#1a1a1a", width: 250, borderRadius: 16, overflow: "hidden" }}>
            <Text style={{ color: "#fff", fontSize: 16, fontWeight: "700", padding: 16, textAlign: "center" }}>⚡ Speed</Text>
            {SPEEDS.map(sp => (
              <TouchableOpacity key={sp} style={[{ padding: 14, borderTopWidth: 0.5, borderColor: "#333" }, speed === sp && { backgroundColor: "#FF6B00" }]} onPress={() => { setSpeed(sp); videoRef.current?.setRateAsync(sp, true); setShowSpeed(false); }}>
                <Text style={{ color: "#fff", textAlign: "center" }}>{sp}x {sp === 1 ? "(Normal)" : ""}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );

  if (screen === "history") return (
    <View style={{ flex: 1, backgroundColor: "#000" }}>
      <View style={s.header}>
        <TouchableOpacity onPress={() => setScreen("home")}><Text style={s.back}>←</Text></TouchableOpacity>
        <Text style={{ color: "#fff", fontSize: 18, fontWeight: "700" }}>🕐 History</Text>
        <TouchableOpacity onPress={() => { setHistory([]); AsyncStorage.removeItem("history"); }}>
          <Text style={{ color: "#f44" }}>Clear</Text>
        </TouchableOpacity>
      </View>
      {history.length === 0 ? (
        <View style={s.empty}><Text style={{ fontSize: 50 }}>🕐</Text><Text style={{ color: "#888" }}>No history</Text></View>
      ) : (
        <FlatList data={history} keyExtractor={(x, i) => x.id + i} contentContainerStyle={{ padding: 12 }} renderItem={({ item, index }) => (
          <TouchableOpacity style={s.card} onPress={() => play(item, index)}>
            <Text style={{ fontSize: 28 }}>🎥</Text>
            <Text style={s.cardTxt} numberOfLines={1}>{item.name}</Text>
          </TouchableOpacity>
        )} />
      )}
    </View>
  );

  if (screen === "network") return (
    <View style={{ flex: 1, backgroundColor: "#000", padding: 20 }}>
      <View style={s.header}>
        <TouchableOpacity onPress={() => setScreen("home")}><Text style={s.back}>←</Text></TouchableOpacity>
        <Text style={{ color: "#fff", fontSize: 18, fontWeight: "700" }}>🌐 Network</Text>
      </View>
      <Text style={{ color: "#888", marginTop: 16, marginBottom: 8 }}>Video URL பேஸ்ட் பண்ணு:</Text>
      <TextInput style={{ backgroundColor: "#111", color: "#fff", borderRadius: 12, padding: 14, fontSize: 14, borderWidth: 1, borderColor: "#FF6B00" }} placeholder="https://..." placeholderTextColor="#666" value={netUrl} onChangeText={setNetUrl} autoCapitalize="none" />
      <TouchableOpacity style={{ backgroundColor: "#FF6B00", padding: 16, borderRadius: 12, alignItems: "center", marginTop: 12 }} onPress={() => { if (netUrl.trim()) play({ id: "net" + Date.now(), uri: netUrl.trim(), name: "Stream" }, 0); }}>
        <Text style={{ color: "#fff", fontSize: 16, fontWeight: "700" }}>▶ Play</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={{ flex: 1, backgroundColor: "#000" }}>
      <StatusBar barStyle="light-content" backgroundColor="#000" />
      <View style={s.header}>
        <Text style={{ color: "#FF6B00", fontSize: 22, fontWeight: "900" }}>⚡ NexPlayer</Text>
        <TouchableOpacity onPress={() => setScreen("history")}><Text style={{ fontSize: 22 }}>🕐</Text></TouchableOpacity>
      </View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ paddingHorizontal: 12, paddingVertical: 8, maxHeight: 56 }}>
        <TouchableOpacity style={[s.aBtn, { backgroundColor: "#FF6B00" }]} onPress={pickVideo}><Text style={s.aBtnTxt}>📁 Add</Text></TouchableOpacity>
        <TouchableOpacity style={[s.aBtn, { backgroundColor: "#1a1a1a" }]} onPress={loadGallery}><Text style={s.aBtnTxt}>🖼 Gallery</Text></TouchableOpacity>
        <TouchableOpacity style={[s.aBtn, { backgroundColor: "#1a1a1a" }]} onPress={() => setScreen("network")}><Text style={s.aBtnTxt}>🌐 Network</Text></TouchableOpacity>
        <TouchableOpacity style={[s.aBtn, { backgroundColor: "#1a1a1a" }]} onPress={() => setVideos([])}><Text style={[s.aBtnTxt, { color: "#f44" }]}>🗑 Clear</Text></TouchableOpacity>
      </ScrollView>
      {videos.length === 0 ? (
        <View style={s.empty}>
          <Text style={{ fontSize: 64 }}>🎬</Text>
          <Text style={{ color: "#888", marginTop: 8, fontSize: 16 }}>No videos yet</Text>
          <Text style={{ color: "#555", fontSize: 13 }}>Add or Gallery tap பண்ணு</Text>
        </View>
      ) : (
        <FlatList data={videos} keyExtractor={x => String(x.id)} contentContainerStyle={{ padding: 12 }} renderItem={({ item, index }) => (
          <TouchableOpacity style={s.card} onPress={() => play(item, index)}>
            <View style={{ width: 64, height: 48, backgroundColor: "#111", borderRadius: 8, justifyContent: "center", alignItems: "center" }}>
              <Text style={{ fontSize: 26 }}>🎥</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={s.cardTxt} numberOfLines={2}>{item.name}</Text>
              {item.duration ? <Text style={{ color: "#888", fontSize: 12 }}>{fmt(item.duration * 1000)}</Text> : null}
            </View>
            <TouchableOpacity onPress={() => setVideos(p => p.filter(v => v.id !== item.id))}>
              <Text style={{ color: "#f44", fontSize: 18, padding: 8 }}>✕</Text>
            </TouchableOpacity>
          </TouchableOpacity>
        )} />
      )}
    </View>
  );
}

const s = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: 16, paddingTop: 44, paddingBottom: 12, backgroundColor: "#111" },
  back: { color: "#fff", fontSize: 18, marginRight: 8 },
  card: { flexDirection: "row", alignItems: "center", backgroundColor: "#111", borderRadius: 12, padding: 12, marginBottom: 8, gap: 12 },
  cardTxt: { color: "#fff", fontSize: 14, fontWeight: "600" },
  aBtn: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, marginRight: 8 },
  aBtnTxt: { color: "#fff", fontWeight: "700", fontSize: 13 },
  empty: { flex: 1, justifyContent: "center", alignItems: "center", gap: 8 },
  overlay: { ...StyleSheet.absoluteFillObject, backgroundColor: "rgba(0,0,0,0.55)", justifyContent: "space-between" },
  topBar: { flexDirection: "row", alignItems: "center", paddingTop: 44, paddingHorizontal: 16, paddingBottom: 8 },
  title: { flex: 1, color: "#fff", fontSize: 13 },
  center: { flexDirection: "row", justifyContent: "center", alignItems: "center", gap: 20 },
  btn: { fontSize: 32, color: "#fff" },
  prog: { flexDirection: "row", alignItems: "center", paddingHorizontal: 16, gap: 8 },
  time: { color: "#fff", fontSize: 12, width: 44, textAlign: "center" },
  bot: { flexDirection: "row", justifyContent: "space-around", paddingBottom: 28, paddingTop: 8 },
  botBtn: { backgroundColor: "rgba(255,255,255,0.15)", paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20 },
  botTxt: { color: "#fff", fontWeight: "700", fontSize: 12 },
  modalBg: { flex: 1, backgroundColor: "rgba(0,0,0,0.7)", justifyContent: "center", alignItems: "center" },
});
'''
f = open("App.tsx", "w")
f.write(code)
f.close()
print("Done! Stable NexPlayer written.")
