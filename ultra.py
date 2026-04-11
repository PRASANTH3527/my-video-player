f = open('App.tsx', 'w')
f.write("""import React, { useState, useRef, useEffect } from "react";
import { View, Text, StyleSheet, TouchableOpacity, FlatList, StatusBar, Dimensions, ScrollView, TextInput, Modal, Alert, PanResponder } from "react-native";
import { Video, ResizeMode } from "expo-av";
import * as DocumentPicker from "expo-document-picker";
import * as MediaLibrary from "expo-media-library";
import AsyncStorage from "@react-native-async-storage/async-storage";

const { width: W, height: H } = Dimensions.get("window");
const SPEEDS = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0];
const THEMES = {
  AMOLED: { bg: "#000", surface: "#0d0d0d", card: "#161616", accent: "#FF6B00", text: "#fff", sub: "#888", border: "#222" },
  DARK: { bg: "#121212", surface: "#1e1e1e", card: "#252525", accent: "#FF6B00", text: "#fff", sub: "#888", border: "#333" },
  BLUE: { bg: "#0a0e1a", surface: "#111827", card: "#1a2234", accent: "#3B82F6", text: "#fff", sub: "#6B7280", border: "#1f2937" },
  PURPLE: { bg: "#0d0a1a", surface: "#1a1025", card: "#241535", accent: "#8B5CF6", text: "#fff", sub: "#9CA3AF", border: "#2d1f3d" },
  RED: { bg: "#1a0000", surface: "#2d0a0a", card: "#3d1212", accent: "#EF4444", text: "#fff", sub: "#9CA3AF", border: "#4d1a1a" },
};
""")
f.close()
print("Part 1 done!")
f = open('App.tsx', 'a')
f.write("""
export default function App() {
  const [tab, setTab] = useState("home");
  const [screen, setScreen] = useState("home");
  const [videos, setVideos] = useState([]);
  const [folders, setFolders] = useState([]);
  const [current, setCurrent] = useState(null);
  const [playing, setPlaying] = useState(false);
  const [pos, setPos] = useState(0);
  const [dur, setDur] = useState(0);
  const [speed, setSpeed] = useState(1.0);
  const [loop, setLoop] = useState("none");
  const [showCtrl, setShowCtrl] = useState(true);
  const [showSpeed, setShowSpeed] = useState(false);
  const [showInfo, setShowInfo] = useState(false);
  const [showSleep, setShowSleep] = useState(false);
  const [showTheme, setShowTheme] = useState(false);
  const [history, setHistory] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [netUrl, setNetUrl] = useState("");
  const [idx, setIdx] = useState(0);
  const [locked, setLocked] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [theme, setTheme] = useState(THEMES.AMOLED);
  const [themeName, setThemeName] = useState("AMOLED");
  const [sleepMin, setSleepMin] = useState(0);
  const [volume, setVolume] = useState(1.0);
  const [showVol, setShowVol] = useState(false);
  const [showBri, setShowBri] = useState(false);
  const [dtLeft, setDtLeft] = useState(false);
  const [dtRight, setDtRight] = useState(false);
  const [search, setSearch] = useState("");
  const [showSearch, setShowSearch] = useState(false);
  const [resumePos, setResumePos] = useState({});
  const videoRef = useRef(null);
  const sleepRef = useRef(null);
  const lastTap = useRef({ t: 0 });
  const swipeRef = useRef({ y: 0, x: 0, side: null });
  const ctrlTimer = useRef(null);
""")
f.close()
print("Part 2 done!")
f = open('App.tsx', 'a')
f.write("""
  useEffect(() => {
    loadData();
    MediaLibrary.requestPermissionsAsync();
  }, []);

  const loadData = async () => {
    try {
      const h = await AsyncStorage.getItem("history"); if (h) setHistory(JSON.parse(h));
      const fav = await AsyncStorage.getItem("favorites"); if (fav) setFavorites(JSON.parse(fav));
      const t = await AsyncStorage.getItem("theme"); if (t) { setThemeName(t); setTheme(THEMES[t]); }
      const r = await AsyncStorage.getItem("resume"); if (r) setResumePos(JSON.parse(r));
    } catch (e) {}
  };

  const fmt = ms => {
    const s = Math.floor(ms / 1000), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
    return h > 0 ? h + ":" + String(m).padStart(2, "0") + ":" + String(sec).padStart(2, "0") : m + ":" + String(sec).padStart(2, "0");
  };

  const resetCtrl = () => {
    if (ctrlTimer.current) clearTimeout(ctrlTimer.current);
    setShowCtrl(true);
    ctrlTimer.current = setTimeout(() => setShowCtrl(false), 4000);
  };

  const play = async (v, i) => {
    setCurrent(v); setIdx(i || 0); setScreen("player"); setPlaying(true); setShowCtrl(true);
    const h = [v, ...history.filter(x => x.id !== v.id)].slice(0, 50);
    setHistory(h); AsyncStorage.setItem("history", JSON.stringify(h));
    if (resumePos[v.id]) setTimeout(() => videoRef.current?.setPositionAsync(resumePos[v.id]), 1000);
  };

  const saveResume = async (id, position) => {
    const r = { ...resumePos, [id]: position };
    setResumePos(r); AsyncStorage.setItem("resume", JSON.stringify(r));
  };

  const toggleFav = v => {
    const isFav = favorites.find(f => f.id === v.id);
    const newFavs = isFav ? favorites.filter(f => f.id !== v.id) : [...favorites, v];
    setFavorites(newFavs); AsyncStorage.setItem("favorites", JSON.stringify(newFavs));
  };

  const pickVideo = async () => {
    try {
      const r = await DocumentPicker.getDocumentAsync({ type: "video/*", multiple: true });
      if (!r.canceled && r.assets) setVideos(p => [...p, ...r.assets.map(a => ({ id: Date.now() + Math.random(), uri: a.uri, name: a.name || "Video" }))]);
    } catch (e) {}
  };

  const loadGallery = async () => {
    try {
      const { assets } = await MediaLibrary.getAssetsAsync({ mediaType: "video", first: 500 });
      const folderMap = {};
      assets.forEach(a => {
        const parts = a.uri.split("/"); const folder = parts[parts.length - 2] || "Videos";
        if (!folderMap[folder]) folderMap[folder] = [];
        folderMap[folder].push({ id: a.id, uri: a.uri, name: a.filename, duration: a.duration });
      });
      setFolders(Object.entries(folderMap).map(([name, vids]) => ({ name, videos: vids, count: vids.length })));
      setVideos(p => { const ids = new Set(p.map(v => v.id)); return [...p, ...assets.filter(a => !ids.has(a.id)).map(a => ({ id: a.id, uri: a.uri, name: a.filename, duration: a.duration }))]; });
    } catch (e) {}
  };

  const onStatus = s => {
    if (s.isLoaded) {
      setPos(s.positionMillis || 0); setDur(s.durationMillis || 0); setPlaying(s.isPlaying);
      if (current && s.positionMillis) saveResume(current.id, s.positionMillis);
      if (s.didJustFinish) {
        if (loop === "one") videoRef.current?.replayAsync();
        else if (loop === "all" && videos.length > 0) { const n = (idx + 1) % videos.length; play(videos[n], n); }
        else if (idx < videos.length - 1) play(videos[idx + 1], idx + 1);
      }
    }
  };

  const handleTap = x => {
    const now = Date.now();
    if (now - lastTap.current.t < 300) {
      if (x < W / 2) { videoRef.current?.setPositionAsync(Math.max(0, pos - 10000)); setDtLeft(true); setTimeout(() => setDtLeft(false), 600); }
      else { videoRef.current?.setPositionAsync(Math.min(dur, pos + 10000)); setDtRight(true); setTimeout(() => setDtRight(false), 600); }
    } else { if (!locked) resetCtrl(); }
    lastTap.current = { t: now };
  };

  const panResponder = PanResponder.create({
    onStartShouldSetPanResponder: () => true,
    onPanResponderGrant: e => { swipeRef.current = { x: e.nativeEvent.pageX, y: e.nativeEvent.pageY, side: e.nativeEvent.pageX < W / 2 ? "left" : "right" }; },
    onPanResponderMove: (e, gs) => {
      if (Math.abs(gs.dy) < 5) return;
      const d = -gs.dy / H;
      if (swipeRef.current.side === "right") { const nv = Math.max(0, Math.min(1, volume + d)); setVolume(nv); videoRef.current?.setVolumeAsync(nv); setShowVol(true); }
      else setShowBri(true);
    },
    onPanResponderRelease: () => setTimeout(() => { setShowVol(false); setShowBri(false); }, 1500),
  });

  const startSleep = m => {
    if (sleepRef.current) clearTimeout(sleepRef.current);
    setSleepMin(m); setShowSleep(false);
    if (m > 0) sleepRef.current = setTimeout(() => { videoRef.current?.pauseAsync(); setPlaying(false); Alert.alert("Sleep Timer", "Video paused!"); }, m * 60000);
  };

  const pct = dur > 0 ? (pos / dur) * 100 : 0;
  const filtered = videos.filter(v => v.name?.toLowerCase().includes(search.toLowerCase()));
""")
f.close()
print("Part 3 done!")
f = open('App.tsx', 'a')
f.write("""
  if (screen === "player" && current) return (
    <View style={{ flex: 1, backgroundColor: "#000" }}>
      <StatusBar hidden />
      <TouchableOpacity activeOpacity={1} style={{ flex: 1 }} onPress={e => handleTap(e.nativeEvent.pageX)} {...panResponder.panHandlers}>
        <Video ref={videoRef} source={{ uri: current.uri }} style={{ flex: 1 }} resizeMode={fullscreen ? ResizeMode.COVER : ResizeMode.CONTAIN} shouldPlay={playing} rate={speed} volume={volume} isLooping={loop === "one"} onPlaybackStatusUpdate={onStatus} />
      </TouchableOpacity>
      {dtLeft && <View style={[st.seekInd, { left: 40 }]}><Text style={st.seekTxt}>⏪ -10s</Text></View>}
      {dtRight && <View style={[st.seekInd, { right: 40 }]}><Text style={st.seekTxt}>+10s ⏩</Text></View>}
      {showVol && <View style={[st.sideBar, { right: 16 }]}><Text style={{ fontSize: 20 }}>🔊</Text><View style={st.barTrack}><View style={[st.barFill, { height: (volume * 100) + "%" }]} /></View><Text style={st.barVal}>{Math.round(volume * 100)}%</Text></View>}
      {showCtrl && !locked && (
        <View style={st.overlay}>
          <View style={st.topGrad}>
            <TouchableOpacity onPress={() => { setScreen("home"); setPlaying(false); setFullscreen(false); }} style={st.backBtn}>
              <Text style={st.backIco}>‹</Text>
            </TouchableOpacity>
            <View style={{ flex: 1 }}>
              <Text style={st.vidTitle} numberOfLines={1}>{current.name}</Text>
              <Text style={st.vidSub}>{fmt(pos)} / {fmt(dur)}</Text>
            </View>
            <TouchableOpacity onPress={() => setShowInfo(true)} style={st.iconBtn}><Text style={{ fontSize: 22 }}>ℹ️</Text></TouchableOpacity>
            <TouchableOpacity onPress={() => setShowSleep(true)} style={st.iconBtn}><Text style={{ fontSize: 22 }}>😴</Text></TouchableOpacity>
            <TouchableOpacity onPress={() => setShowTheme(true)} style={st.iconBtn}><Text style={{ fontSize: 22 }}>🎨</Text></TouchableOpacity>
            <TouchableOpacity onPress={() => setFullscreen(f => !f)} style={st.iconBtn}><Text style={{ fontSize: 22 }}>{fullscreen ? "⊡" : "⛶"}</Text></TouchableOpacity>
          </View>
          <View style={st.centerRow}>
            <TouchableOpacity onPress={() => { if (idx > 0) play(videos[idx - 1], idx - 1); }} style={st.ctrlBtn}><Text style={st.ctrlIco}>⏮</Text></TouchableOpacity>
            <TouchableOpacity onPress={() => videoRef.current?.setPositionAsync(Math.max(0, pos - 10000))} style={st.ctrlBtn}><Text style={st.ctrlIco}>⏪</Text><Text style={st.ctrlLbl}>10s</Text></TouchableOpacity>
            <TouchableOpacity onPress={() => { playing ? videoRef.current?.pauseAsync() : videoRef.current?.playAsync(); setPlaying(!playing); }} style={st.playBtn}>
              <Text style={st.playIco}>{playing ? "⏸" : "▶"}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => videoRef.current?.setPositionAsync(Math.min(dur, pos + 10000))} style={st.ctrlBtn}><Text style={st.ctrlIco}>⏩</Text><Text style={st.ctrlLbl}>10s</Text></TouchableOpacity>
            <TouchableOpacity onPress={() => { if (idx < videos.length - 1) play(videos[idx + 1], idx + 1); }} style={st.ctrlBtn}><Text style={st.ctrlIco}>⏭</Text></TouchableOpacity>
          </View>
          <View style={st.botGrad}>
            <View style={st.progRow}>
              <Text style={st.timeL}>{fmt(pos)}</Text>
              <TouchableOpacity style={st.progTrack} onPress={e => videoRef.current?.setPositionAsync((e.nativeEvent.locationX / (W - 100)) * dur)}>
                <View style={st.progBg}>
                  <View style={[st.progFill, { width: pct + "%" }]} />
                  <View style={[st.progDot, { left: pct + "%" }]} />
                </View>
              </TouchableOpacity>
              <Text style={st.timeR}>{fmt(dur)}</Text>
            </View>
            <View style={st.botBtns}>
              <TouchableOpacity onPress={() => setLocked(true)} style={st.chip}><Text style={st.chipTxt}>🔒 Lock</Text></TouchableOpacity>
              <TouchableOpacity onPress={() => setShowSpeed(true)} style={st.chip}><Text style={st.chipTxt}>⚡ {speed}x</Text></TouchableOpacity>
              <TouchableOpacity onPress={() => setLoop(l => l === "none" ? "one" : l === "one" ? "all" : "none")} style={st.chip}><Text style={st.chipTxt}>{loop === "none" ? "🔁" : loop === "one" ? "🔂" : "🔃"}</Text></TouchableOpacity>
              <TouchableOpacity onPress={() => toggleFav(current)} style={st.chip}><Text style={st.chipTxt}>{favorites.find(f => f.id === current?.id) ? "❤️" : "🤍"}</Text></TouchableOpacity>
              <TouchableOpacity onPress={pickVideo} style={st.chip}><Text style={st.chipTxt}>＋ Add</Text></TouchableOpacity>
            </View>
          </View>
        </View>
      )}
      {locked && <TouchableOpacity style={st.lockScreen} onPress={() => setLocked(false)}><View style={st.lockBox}><Text style={{ fontSize: 40 }}>🔒</Text><Text style={{ color: "#fff", marginTop: 12 }}>Tap to unlock</Text></View></TouchableOpacity>}
""")
f.close()
print("Part 4 done!")
f = open('App.tsx', 'a')
f.write("""
      <Modal visible={showSpeed} transparent animationType="slide"><TouchableOpacity style={st.modalBg} onPress={() => setShowSpeed(false)}><View style={[st.sheet, { backgroundColor: theme.surface }]}><View style={st.handle} /><Text style={[st.sheetTitle, { color: theme.text }]}>⚡ Speed</Text>{SPEEDS.map(sp => (<TouchableOpacity key={sp} style={[st.sheetRow, sp === speed && { backgroundColor: theme.accent + "22" }]} onPress={() => { setSpeed(sp); videoRef.current?.setRateAsync(sp, true); setShowSpeed(false); }}><Text style={[st.sheetRowTxt, { color: sp === speed ? theme.accent : theme.text }]}>{sp === 1.0 ? "Normal (1x)" : sp + "x"}</Text>{sp === speed && <Text style={{ color: theme.accent }}>✓</Text>}</TouchableOpacity>))}</View></TouchableOpacity></Modal>
      <Modal visible={showSleep} transparent animationType="slide"><TouchableOpacity style={st.modalBg} onPress={() => setShowSleep(false)}><View style={[st.sheet, { backgroundColor: theme.surface }]}><View style={st.handle} /><Text style={[st.sheetTitle, { color: theme.text }]}>😴 Sleep Timer</Text>{[5,10,15,20,30,45,60,90].map(m => (<TouchableOpacity key={m} style={[st.sheetRow, sleepMin === m && { backgroundColor: theme.accent + "22" }]} onPress={() => startSleep(m)}><Text style={[st.sheetRowTxt, { color: sleepMin === m ? theme.accent : theme.text }]}>{m} minutes</Text>{sleepMin === m && <Text style={{ color: theme.accent }}>✓</Text>}</TouchableOpacity>))}<TouchableOpacity style={st.sheetRow} onPress={() => startSleep(0)}><Text style={[st.sheetRowTxt, { color: "#f44" }]}>Cancel Timer</Text></TouchableOpacity></View></TouchableOpacity></Modal>
      <Modal visible={showInfo} transparent animationType="fade"><TouchableOpacity style={st.modalBg} onPress={() => setShowInfo(false)}><View style={[st.sheet, { backgroundColor: theme.surface }]}><View style={st.handle} /><Text style={[st.sheetTitle, { color: theme.text }]}>ℹ️ Info</Text><Text style={[st.infoTxt, { color: theme.sub }]}>📄 {current?.name}</Text><Text style={[st.infoTxt, { color: theme.sub }]}>⏱ {fmt(dur)}</Text><Text style={[st.infoTxt, { color: theme.sub }]}>📍 {fmt(pos)}</Text><Text style={[st.infoTxt, { color: theme.sub }]}>⚡ {speed}x</Text><Text style={[st.infoTxt, { color: theme.sub }]}>🔁 {loop}</Text><Text style={[st.infoTxt, { color: theme.sub }]}>🔊 {Math.round(volume * 100)}%</Text></View></TouchableOpacity></Modal>
      <Modal visible={showTheme} transparent animationType="slide"><TouchableOpacity style={st.modalBg} onPress={() => setShowTheme(false)}><View style={[st.sheet, { backgroundColor: theme.surface }]}><View style={st.handle} /><Text style={[st.sheetTitle, { color: theme.text }]}>🎨 Theme</Text>{Object.keys(THEMES).map(t => (<TouchableOpacity key={t} style={[st.sheetRow, themeName === t && { backgroundColor: THEMES[t].accent + "22" }]} onPress={() => { setThemeName(t); setTheme(THEMES[t]); AsyncStorage.setItem("theme", t); setShowTheme(false); }}><View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}><View style={{ width: 24, height: 24, borderRadius: 12, backgroundColor: THEMES[t].accent }} /><Text style={[st.sheetRowTxt, { color: themeName === t ? THEMES[t].accent : theme.text }]}>{t}</Text></View>{themeName === t && <Text style={{ color: THEMES[t].accent }}>✓</Text>}</TouchableOpacity>))}</View></TouchableOpacity></Modal>
    </View>
  );
""")
f.close()
print("Part 5 done!")
f = open('App.tsx', 'a')
f.write("""
  return (
    <View style={{ flex: 1, backgroundColor: theme.bg }}>
      <StatusBar barStyle="light-content" backgroundColor={theme.bg} />
      <View style={[hd.header, { backgroundColor: theme.surface }]}>
        <View><Text style={[hd.appName, { color: theme.accent }]}>⚡ NexPlayer</Text><Text style={[hd.appSub, { color: theme.sub }]}>Pro Edition</Text></View>
        <View style={{ flexDirection: "row", gap: 12 }}>
          <TouchableOpacity onPress={() => setShowSearch(!showSearch)}><Text style={{ fontSize: 22 }}>🔍</Text></TouchableOpacity>
          <TouchableOpacity onPress={loadGallery}><Text style={{ fontSize: 22 }}>📂</Text></TouchableOpacity>
        </View>
      </View>
      {showSearch && <TextInput style={[hd.searchBox, { backgroundColor: theme.card, color: theme.text, borderColor: theme.border }]} placeholder="Search videos..." placeholderTextColor={theme.sub} value={search} onChangeText={setSearch} />}
      <View style={[hd.tabs, { backgroundColor: theme.surface, borderBottomColor: theme.border }]}>
        {[["home","🏠","Home"],["folders","📁","Folders"],["fav","❤️","Favs"],["history","🕐","History"],["network","🌐","Stream"]].map(([t,ic,lb]) => (
          <TouchableOpacity key={t} style={[hd.tab, tab === t && { borderBottomColor: theme.accent, borderBottomWidth: 2 }]} onPress={() => setTab(t)}>
            <Text style={{ fontSize: 18 }}>{ic}</Text>
            <Text style={[hd.tabLbl, { color: tab === t ? theme.accent : theme.sub }]}>{lb}</Text>
          </TouchableOpacity>
        ))}
      </View>
      {tab === "home" && (
        <View style={{ flex: 1 }}>
          <View style={[hd.actionBar, { backgroundColor: theme.bg }]}>
            <TouchableOpacity style={[hd.addBtn, { backgroundColor: theme.accent }]} onPress={pickVideo}><Text style={hd.addBtnTxt}>＋ Add</Text></TouchableOpacity>
            <TouchableOpacity style={[hd.addBtn, { backgroundColor: theme.card }]} onPress={loadGallery}><Text style={[hd.addBtnTxt, { color: theme.text }]}>📂 Gallery</Text></TouchableOpacity>
            <TouchableOpacity onPress={() => setVideos([])}><Text style={{ color: "#f44", fontSize: 13 }}>🗑 Clear</Text></TouchableOpacity>
          </View>
          {filtered.length === 0 ? (
            <View style={hd.empty}>
              <Text style={{ fontSize: 72 }}>🎬</Text>
              <Text style={[hd.emptyTitle, { color: theme.text }]}>No Videos Yet</Text>
              <Text style={[hd.emptySub, { color: theme.sub }]}>Add videos or import from Gallery</Text>
              <TouchableOpacity style={[hd.emptyBtn, { backgroundColor: theme.accent }]} onPress={pickVideo}><Text style={{ color: "#fff", fontWeight: "800" }}>＋ Add Video</Text></TouchableOpacity>
            </View>
          ) : (
            <FlatList data={filtered} keyExtractor={x => String(x.id)} contentContainerStyle={{ padding: 12, gap: 8 }} renderItem={({ item, index }) => (
              <TouchableOpacity style={[hd.card, { backgroundColor: theme.card }]} onPress={() => play(item, index)}>
                <View style={[hd.thumb, { backgroundColor: theme.surface }]}>
                  <Text style={{ fontSize: 28 }}>🎥</Text>
                  {item.duration && <View style={hd.durBadge}><Text style={hd.durTxt}>{fmt(item.duration * 1000)}</Text></View>}
                  {resumePos[item.id] && <View style={[hd.durBadge, { bottom: "auto", top: 4, backgroundColor: theme.accent + "cc" }]}><Text style={hd.durTxt}>▶ Resume</Text></View>}
                </View>
                <View style={{ flex: 1, gap: 4 }}>
                  <Text style={[hd.cardTitle, { color: theme.text }]} numberOfLines={2}>{item.name}</Text>
                  <Text style={[hd.cardSub, { color: theme.sub }]}>{item.duration ? fmt(item.duration * 1000) : "Tap to play"}</Text>
                </View>
                <View style={{ gap: 8, alignItems: "center" }}>
                  <TouchableOpacity onPress={() => play(item, index)} style={[hd.playBtn, { backgroundColor: theme.accent }]}><Text style={{ color: "#fff", fontSize: 14 }}>▶</Text></TouchableOpacity>
                  <TouchableOpacity onPress={() => toggleFav(item)}><Text style={{ fontSize: 18 }}>{favorites.find(f => f.id === item.id) ? "❤️" : "🤍"}</Text></TouchableOpacity>
                  <TouchableOpacity onPress={() => setVideos(p => p.filter(v => v.id !== item.id))}><Text style={{ color: "#f44", fontSize: 16 }}>✕</Text></TouchableOpacity>
                </View>
              </TouchableOpacity>
            )} />
          )}
        </View>
      )}
      {tab === "folders" && (
        <View style={{ flex: 1 }}>
          {folders.length === 0 ? (
            <View style={hd.empty}><Text style={{ fontSize: 64 }}>📁</Text><Text style={[hd.emptyTitle, { color: theme.text }]}>No Folders</Text><TouchableOpacity style={[hd.emptyBtn, { backgroundColor: theme.accent }]} onPress={loadGallery}><Text style={{ color: "#fff", fontWeight: "800" }}>📂 Load Gallery</Text></TouchableOpacity></View>
          ) : (
            <FlatList data={folders} keyExtractor={x => x.name} contentContainerStyle={{ padding: 12, gap: 8 }} renderItem={({ item }) => (
              <TouchableOpacity style={[hd.card, { backgroundColor: theme.card }]} onPress={() => { setVideos(item.videos); setTab("home"); }}>
                <Text style={{ fontSize: 40 }}>📁</Text>
                <View style={{ flex: 1 }}><Text style={[hd.cardTitle, { color: theme.text }]}>{item.name}</Text><Text style={[hd.cardSub, { color: theme.sub }]}>{item.count} videos</Text></View>
                <Text style={{ color: theme.accent, fontSize: 22 }}>›</Text>
              </TouchableOpacity>
            )} />
          )}
        </View>
      )}
      {tab === "fav" && (
        <View style={{ flex: 1 }}>
          {favorites.length === 0 ? (
            <View style={hd.empty}><Text style={{ fontSize: 64 }}>❤️</Text><Text style={[hd.emptyTitle, { color: theme.text }]}>No Favorites</Text><Text style={[hd.emptySub, { color: theme.sub }]}>Tap ❤️ on any video</Text></View>
          ) : (
            <FlatList data={favorites} keyExtractor={(x,i) => x.id+i} contentContainerStyle={{ padding: 12, gap: 8 }} renderItem={({ item, index }) => (
              <TouchableOpacity style={[hd.card, { backgroundColor: theme.card }]} onPress={() => play(item, index)}>
                <View style={[hd.thumb, { backgroundColor: theme.surface }]}><Text style={{ fontSize: 28 }}>🎥</Text></View>
                <View style={{ flex: 1 }}><Text style={[hd.cardTitle, { color: theme.text }]} numberOfLines={2}>{item.name}</Text></View>
                <Text style={{ color: theme.accent, fontSize: 22 }}>▶</Text>
              </TouchableOpacity>
            )} />
          )}
        </View>
      )}
      {tab === "history" && (
        <View style={{ flex: 1 }}>
          <View style={[hd.actionBar, { backgroundColor: theme.bg }]}>
            <Text style={{ color: theme.sub, fontSize: 13 }}>{history.length} videos</Text>
            <TouchableOpacity onPress={() => { setHistory([]); AsyncStorage.removeItem("history"); }}><Text style={{ color: "#f44", fontSize: 13 }}>Clear All</Text></TouchableOpacity>
          </View>
          {history.length === 0 ? (
            <View style={hd.empty}><Text style={{ fontSize: 64 }}>🕐</Text><Text style={[hd.emptyTitle, { color: theme.text }]}>No History</Text></View>
          ) : (
            <FlatList data={history} keyExtractor={(x,i) => x.id+i} contentContainerStyle={{ padding: 12, gap: 8 }} renderItem={({ item, index }) => (
              <TouchableOpacity style={[hd.card, { backgroundColor: theme.card }]} onPress={() => play(item, index)}>
                <View style={[hd.thumb, { backgroundColor: theme.surface }]}><Text style={{ fontSize: 28 }}>🎥</Text></View>
                <View style={{ flex: 1 }}><Text style={[hd.cardTitle, { color: theme.text }]} numberOfLines={2}>{item.name}</Text><Text style={[hd.cardSub, { color: theme.sub }]}>Recently watched</Text></View>
                <Text style={{ color: theme.accent, fontSize: 22 }}>▶</Text>
              </TouchableOpacity>
            )} />
          )}
        </View>
      )}
      {tab === "network" && (
        <ScrollView style={{ flex: 1, padding: 20 }}>
          <Text style={[hd.netTitle, { color: theme.text }]}>🌐 Stream Online</Text>
          <Text style={[hd.netSub, { color: theme.sub }]}>Enter video URL or stream link</Text>
          <TextInput style={[hd.urlInput, { backgroundColor: theme.card, color: theme.text, borderColor: theme.border }]} placeholder="https://example.com/video.mp4" placeholderTextColor={theme.sub} value={netUrl} onChangeText={setNetUrl} autoCapitalize="none" multiline />
          <TouchableOpacity style={[hd.streamBtn, { backgroundColor: theme.accent }]} onPress={() => { if (netUrl.trim()) play({ id: "net"+Date.now(), uri: netUrl.trim(), name: "Network Stream" }, 0); }}>
            <Text style={hd.streamBtnTxt}>▶ Play Stream</Text>
          </TouchableOpacity>
          <View style={[hd.supportBox, { backgroundColor: theme.card, borderColor: theme.border }]}>
            <Text style={[hd.supportTitle, { color: theme.sub }]}>Supported Formats</Text>
            <Text style={[hd.supportTxt, { color: theme.sub }]}>MP4 • MKV • M3U8 • HLS • RTSP • AVI • MOV</Text>
          </View>
        </ScrollView>
      )}
    </View>
  );
}
""")
f.close()
print("Part 6 done!")
f = open('App.tsx', 'a')
f.write("""
const st = StyleSheet.create({
  overlay: { ...StyleSheet.absoluteFillObject, justifyContent: "space-between" },
  topGrad: { flexDirection: "row", alignItems: "center", paddingTop: 44, paddingHorizontal: 12, paddingBottom: 12, backgroundColor: "rgba(0,0,0,0.75)", gap: 4 },
  backBtn: { width: 44, height: 44, justifyContent: "center", alignItems: "center" },
  backIco: { color: "#fff", fontSize: 40, fontWeight: "200" },
  vidTitle: { color: "#fff", fontSize: 13, fontWeight: "700" },
  vidSub: { color: "rgba(255,255,255,0.5)", fontSize: 11, marginTop: 2 },
  iconBtn: { width: 40, height: 40, justifyContent: "center", alignItems: "center" },
  centerRow: { flexDirection: "row", justifyContent: "center", alignItems: "center", gap: 12 },
  ctrlBtn: { alignItems: "center", width: 56, height: 56, justifyContent: "center" },
  ctrlIco: { fontSize: 26, color: "#fff" },
  ctrlLbl: { color: "rgba(255,255,255,0.5)", fontSize: 10 },
  playBtn: { width: 76, height: 76, borderRadius: 38, backgroundColor: "#FF6B00", justifyContent: "center", alignItems: "center", elevation: 8 },
  playIco: { fontSize: 34, color: "#fff" },
  botGrad: { backgroundColor: "rgba(0,0,0,0.75)", paddingBottom: 36, paddingTop: 8, paddingHorizontal: 16 },
  progRow: { flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 12 },
  timeL: { color: "#fff", fontSize: 11, width: 38 },
  timeR: { color: "#fff", fontSize: 11, width: 38, textAlign: "right" },
  progTrack: { flex: 1, height: 24, justifyContent: "center" },
  progBg: { height: 3, backgroundColor: "rgba(255,255,255,0.2)", borderRadius: 2 },
  progFill: { height: 3, backgroundColor: "#FF6B00", borderRadius: 2 },
  progDot: { position: "absolute", top: -5, width: 14, height: 14, borderRadius: 7, backgroundColor: "#FF6B00", marginLeft: -7 },
  botBtns: { flexDirection: "row", gap: 8, flexWrap: "wrap" },
  chip: { backgroundColor: "rgba(255,255,255,0.12)", paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20, borderWidth: 1, borderColor: "rgba(255,255,255,0.08)" },
  chipTxt: { color: "#fff", fontSize: 12, fontWeight: "700" },
  seekInd: { position: "absolute", top: "44%", backgroundColor: "rgba(0,0,0,0.75)", borderRadius: 16, padding: 14 },
  seekTxt: { color: "#fff", fontSize: 15, fontWeight: "800" },
  sideBar: { position: "absolute", top: "22%", alignItems: "center", backgroundColor: "rgba(0,0,0,0.75)", borderRadius: 16, padding: 10, gap: 6 },
  barTrack: { width: 6, height: 110, backgroundColor: "rgba(255,255,255,0.2)", borderRadius: 3, justifyContent: "flex-end", overflow: "hidden" },
  barFill: { width: "100%", backgroundColor: "#FF6B00", borderRadius: 3 },
  barVal: { color: "#fff", fontSize: 11, fontWeight: "700" },
  lockScreen: { ...StyleSheet.absoluteFillObject, backgroundColor: "rgba(0,0,0,0.88)", justifyContent: "center", alignItems: "center" },
  lockBox: { alignItems: "center" },
  modalBg: { flex: 1, backgroundColor: "rgba(0,0,0,0.6)", justifyContent: "flex-end" },
  sheet: { borderTopLeftRadius: 28, borderTopRightRadius: 28, paddingBottom: 44 },
  handle: { width: 44, height: 4, backgroundColor: "#444", borderRadius: 2, alignSelf: "center", marginTop: 14, marginBottom: 6 },
  sheetTitle: { fontSize: 17, fontWeight: "800", padding: 16, paddingBottom: 10 },
  sheetRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: 16, borderTopWidth: 0.5, borderColor: "rgba(255,255,255,0.08)" },
  sheetRowTxt: { fontSize: 15 },
  infoTxt: { fontSize: 14, padding: 8, paddingHorizontal: 16 },
});

const hd = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: 20, paddingTop: 52, paddingBottom: 14 },
  appName: { fontSize: 26, fontWeight: "900", letterSpacing: -0.5 },
  appSub: { fontSize: 11, fontWeight: "700", marginTop: 1 },
  searchBox: { marginHorizontal: 16, marginVertical: 8, padding: 12, borderRadius: 14, borderWidth: 1, fontSize: 14 },
  tabs: { flexDirection: "row", borderBottomWidth: 1, paddingHorizontal: 4 },
  tab: { flex: 1, alignItems: "center", paddingVertical: 10, gap: 2 },
  tabLbl: { fontSize: 10, fontWeight: "700" },
  actionBar: { flexDirection: "row", alignItems: "center", gap: 10, paddingHorizontal: 16, paddingVertical: 10 },
  addBtn: { paddingHorizontal: 16, paddingVertical: 10, borderRadius: 20 },
  addBtnTxt: { color: "#fff", fontWeight: "800", fontSize: 13 },
  empty: { flex: 1, justifyContent: "center", alignItems: "center", gap: 12, paddingBottom: 60 },
  emptyTitle: { fontSize: 20, fontWeight: "800" },
  emptySub: { fontSize: 14 },
  emptyBtn: { paddingHorizontal: 24, paddingVertical: 12, borderRadius: 24, marginTop: 8 },
  card: { flexDirection: "row", alignItems: "center", borderRadius: 16, padding: 12, gap: 12 },
  thumb: { width: 84, height: 58, borderRadius: 12, justifyContent: "center", alignItems: "center", position: "relative" },
  durBadge: { position: "absolute", bottom: 4, right: 4, backgroundColor: "rgba(0,0,0,0.85)", paddingHorizontal: 5, paddingVertical: 2, borderRadius: 5 },
  durTxt: { color: "#fff", fontSize: 10, fontWeight: "700" },
  cardTitle: { fontSize: 14, fontWeight: "700" },
  cardSub: { fontSize: 12 },
  playBtn: { width: 34, height: 34, borderRadius: 17, justifyContent: "center", alignItems: "center" },
  netTitle: { fontSize: 24, fontWeight: "900", marginBottom: 4 },
  netSub: { fontSize: 14, marginBottom: 16 },
  urlInput: { borderRadius: 16, padding: 16, fontSize: 14, borderWidth: 1, minHeight: 90, marginBottom: 14 },
  streamBtn: { padding: 18, borderRadius: 16, alignItems: "center", marginBottom: 20 },
  streamBtnTxt: { color: "#fff", fontSize: 16, fontWeight: "800" },
  supportBox: { borderRadius: 16, padding: 16, borderWidth: 1 },
  supportTitle: { fontSize: 12, fontWeight: "700", marginBottom: 6 },
  supportTxt: { fontSize: 13 },
});
""")
f.close()
print("ALL DONE! Ultimate NexPlayer Pro complete!")
