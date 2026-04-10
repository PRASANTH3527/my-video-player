
import { useState, useRef, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Dimensions, StatusBar } from 'react-native';
import { Video, ResizeMode } from 'expo-av';
import * as DocumentPicker from 'expo-document-picker';

const { width } = Dimensions.get('window');
export default function App() {
  const videoRef = useRef(null);
  const [videoUri, setVideoUri] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1.0);
  const [volume, setVolume] = useState(1.0);
  const [playlist, setPlaylist] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [position, setPosition] = useState(0);
  const [duration, setDuration] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [subtitleText, setSubtitleText] = useState('');
  const [subtitles, setSubtitles] = useState([]);

  useEffect(() => {
    if (subtitles.length > 0) {
      const cur = subtitles.find(s => position >= s.start && position <= s.end);
      setSubtitleText(cur ? cur.text : '');
    }
  }, [position, subtitles]);

  const pickVideo = async () => {
    const result = await DocumentPicker.getDocumentAsync({ type: 'video/*', multiple: true, copyToCacheDirectory: true });
    if (!result.canceled) { setPlaylist(result.assets); setVideoUri(result.assets[0].uri); setCurrentIndex(0); }
  };

  const pickSubtitle = async () => {
    const result = await DocumentPicker.getDocumentAsync({ type: 'text/*', copyToCacheDirectory: true });
    if (!result.canceled) {
      const res = await fetch(result.assets[0].uri);
      const text = await res.text();
      const blocks = text.trim().split(/\n\n/);
      const toMs = (t) => { if (!t) return 0; const p = t.trim().replace(',','.').split(':'); return (parseFloat(p[0])*3600+parseFloat(p[1])*60+parseFloat(p[2]))*1000; };
      const parsed = blocks.map(b => { const l = b.split('\n'); if (l.length < 3) return null; const t = l[1].split(' --> '); return { start: toMs(t[0]), end: toMs(t[1]), text: l.slice(2).join('\n') }; }).filter(Boolean);
      setSubtitles(parsed);
    }
  };

  const togglePlay = async () => {
    if (!videoRef.current) return;
    isPlaying ? await videoRef.current.pauseAsync() : await videoRef.current.playAsync();
    setIsPlaying(!isPlaying);
  };

  const changeSpeed = async (s) => { setSpeed(s); if (videoRef.current) await videoRef.current.setRateAsync(s, true); };
  const formatTime = (ms) => { const s = Math.floor(ms/1000); return Math.floor(s/60)+':'+(s%60).toString().padStart(2,'0'); };
  const playAt = (i) => { setCurrentIndex(i); setVideoUri(playlist[i].uri); setSubtitleText(''); };
  const seek = async (secs) => { if (videoRef.current) await videoRef.current.setPositionAsync(position+secs*1000); };

  return (
    <View style={[s.bg, isFullscreen && s.fs]}>
      <StatusBar hidden={isFullscreen} />
      {!isFullscreen && <Text style={s.title}>NexPlayer</Text>}
      {videoUri ? (
        <TouchableOpacity activeOpacity={1} onPress={() => setShowControls(!showControls)}>
          <View>
            <Video ref={videoRef} source={{uri:videoUri}} style={isFullscreen?s.fsVideo:s.video}
              resizeMode={ResizeMode.CONTAIN} volume={volume} shouldPlay={false}
              onPlaybackStatusUpdate={(st) => { if (st.isLoaded) { setPosition(st.positionMillis); setDuration(st.durationMillis||1); setIsPlaying(st.isPlaying); } }} />
            {subtitleText?<Text style={s.sub}>{subtitleText}</Text>:null}
          </View>
        </TouchableOpacity>
      ) : (
        <TouchableOpacity style={s.box} onPress={pickVideo}>
          <Text style={s.boxIcon}>📂</Text>
          <Text style={s.boxTxt}>Video Select பண்ணு</Text>
        </TouchableOpacity>
      )}
      {videoUri && showControls && (
        <ScrollView style={s.ctrlBox}>
          <Text style={s.time}>{formatTime(position)} / {formatTime(duration)}</Text>
          <View style={s.bar}><View style={[s.fill,{width:`${(position/duration)*100}%`}]} /></View>
          <View style={s.ctrl}>
            <TouchableOpacity onPress={()=>seek(-10)}><Text style={s.ct}>⏪</Text></TouchableOpacity>
            <TouchableOpacity onPress={()=>currentIndex>0&&playAt(currentIndex-1)}><Text style={s.ct}>⏮</Text></TouchableOpacity>
            <TouchableOpacity style={s.playBtn} onPress={togglePlay}><Text style={s.pt}>{isPlaying?'⏸':'▶'}</Text></TouchableOpacity>
            <TouchableOpacity onPress={()=>currentIndex<playlist.length-1&&playAt(currentIndex+1)}><Text style={s.ct}>⏭</Text></TouchableOpacity>
            <TouchableOpacity onPress={()=>seek(10)}><Text style={s.ct}>⏩</Text></TouchableOpacity>
            <TouchableOpacity onPress={()=>setIsFullscreen(!isFullscreen)}><Text style={s.ct}>{isFullscreen?'⬜':'⛶'}</Text></TouchableOpacity>
          </View>
          <View style={s.row}>{[0.5,0.75,1.0,1.25,1.5,2.0].map(sp=>(<TouchableOpacity key={sp} onPress={()=>changeSpeed(sp)} style={[s.chip,speed===sp&&s.on]}><Text style={s.cht}>{sp}x</Text></TouchableOpacity>))}</View>
          <View style={s.row}>{[0.25,0.5,0.75,1.0].map(v=>(<TouchableOpacity key={v} onPress={()=>setVolume(v)} style={[s.chip,volume===v&&s.on]}><Text style={s.cht}>{Math.round(v*100)}%</Text></TouchableOpacity>))}</View>
          <View style={s.actRow}>
            <TouchableOpacity style={s.actBtn} onPress={pickSubtitle}><Text style={s.at}>📝 Subtitle</Text></TouchableOpacity>
            <TouchableOpacity style={s.actBtn} onPress={pickVideo}><Text style={s.at}>+ Video</Text></TouchableOpacity>
            <TouchableOpacity style={s.actBtn} onPress={()=>{setVideoUri(null);setPlaylist([]);}}><Text style={s.at}>🏠 Home</Text></TouchableOpacity>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{marginTop:8}}>
            {playlist.map((f,i)=>(<TouchableOpacity key={i} onPress={()=>playAt(i)} style={[s.pi,i===currentIndex&&s.po]}><Text style={s.pt2} numberOfLines={1}>{f.name}</Text></TouchableOpacity>))}
          </ScrollView>
        </ScrollView>
      )}
    </View>
  );
}

const s = StyleSheet.create({
  bg:{flex:1,backgroundColor:'#0a0a0a'},
  fs:{backgroundColor:'#000'},
  title:{color:'#FF6B00',fontSize:22,fontWeight:'bold',textAlign:'center',paddingTop:40,paddingBottom:8},
  video:{width,height:220,backgroundColor:'#000'},
  fsVideo:{width,height:'100%',backgroundColor:'#000'},
  sub:{position:'absolute',bottom:20,left:0,right:0,textAlign:'center',color:'#fff',fontSize:16,backgroundColor:'rgba(0,0,0,0.6)',padding:4},
  box:{width:width-40,height:200,backgroundColor:'#1a1a1a',borderRadius:14,justifyContent:'center',alignItems:'center',borderWidth:2,borderColor:'#FF6B00',borderStyle:'dashed',marginTop:40,alignSelf:'center'},
  boxIcon:{fontSize:48},
  boxTxt:{color:'#FF6B00',fontSize:15,marginTop:8},
  ctrlBox:{paddingHorizontal:16,paddingTop:8},
  time:{color:'#888',fontSize:12,textAlign:'center'},
  bar:{width:'100%',height:4,backgroundColor:'#333',borderRadius:2,marginTop:4},
  fill:{height:4,backgroundColor:'#FF6B00',borderRadius:2},
  ctrl:{flexDirection:'row',alignItems:'center',justifyContent:'center',gap:14,marginTop:12},
  ct:{fontSize:24,color:'#fff'},
  playBtn:{backgroundColor:'#FF6B00',width:60,height:60,borderRadius:30,justifyContent:'center',alignItems:'center'},
  pt:{fontSize:24,color:'#fff'},
  row:{flexDirection:'row',flexWrap:'wrap',gap:8,marginTop:10,justifyContent:'center'},
  chip:{backgroundColor:'#1a1a1a',paddingHorizontal:10,paddingVertical:5,borderRadius:8,borderWidth:1,borderColor:'#333'},
  on:{borderColor:'#FF6B00',backgroundColor:'#2a1500'},
  cht:{color:'#fff',fontSize:12},
  actRow:{flexDirection:'row',gap:8,marginTop:10,justifyContent:'center'},
  actBtn:{backgroundColor:'#1a1a1a',paddingHorizontal:14,paddingVertical:8,borderRadius:8,borderWidth:1,borderColor:'#FF6B00'},
  at:{color:'#FF6B00',fontSize:12},
  pi:{padding:8,backgroundColor:'#1a1a1a',marginRight:8,borderRadius:8,maxWidth:150},
  po:{backgroundColor:'#2a1500',borderWidth:1,borderColor:'#FF6B00'},
  pt2:{color:'#fff',fontSize:12},
});
