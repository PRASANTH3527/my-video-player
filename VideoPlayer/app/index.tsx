import { useState, useRef } from 'react';
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

  const pickVideo = async () => {
    const result = await DocumentPicker.getDocumentAsync({ type: 'video/*', multiple: true, copyToCacheDirectory: true });
    if (!result.canceled) {
      setPlaylist(result.assets);
      setVideoUri(result.assets[0].uri);
      setCurrentIndex(0);
    }
  };

  const togglePlay = async () => {
    if (!videoRef.current) return;
    isPlaying ? await videoRef.current.pauseAsync() : await videoRef.current.playAsync();
    setIsPlaying(!isPlaying);
  };

  const changeSpeed = async (s) => {
    setSpeed(s);
    if (videoRef.current) await videoRef.current.setRateAsync(s, true);
  };

  const formatTime = (ms) => {
    const s = Math.floor(ms / 1000);
    return Math.floor(s/60) + ':' + (s%60).toString().padStart(2,'0');
  };

  const playAt = async (i) => {
    setCurrentIndex(i);
    setVideoUri(playlist[i].uri);
  };

  return (
    <View style={s.bg}>
      <StatusBar hidden />
      <Text style={s.title}>NexPlayer</Text>
      {videoUri ? (
        <Video ref={videoRef} source={{ uri: videoUri }} style={s.video}
          resizeMode={ResizeMode.CONTAIN} volume={volume} shouldPlay={false}
          useNativeControls
          onPlaybackStatusUpdate={(st) => {
            if (st.isLoaded) { setPosition(st.positionMillis); setDuration(st.durationMillis||1); setIsPlaying(st.isPlaying); }
          }} />
      ) : (
        <TouchableOpacity style={s.box} onPress={pickVideo}>
          <Text style={s.boxIcon}>📂</Text>
          <Text style={s.boxTxt}>Video Select பண்ணு</Text>
        </TouchableOpacity>
      )}
      {videoUri && <>
        <Text style={s.time}>{formatTime(position)} / {formatTime(duration)}</Text>
        <View style={s.bar}><View style={[s.fill,{width:`${(position/duration)*100}%`}]} /></View>
        <View style={s.controls}>
          <TouchableOpacity onPress={()=>currentIndex>0&&playAt(currentIndex-1)}><Text style={s.ctrl}>⏮</Text></TouchableOpacity>
          <TouchableOpacity style={s.playBtn} onPress={togglePlay}><Text style={s.playTxt}>{isPlaying?'⏸':'▶'}</Text></TouchableOpacity>
          <TouchableOpacity onPress={()=>currentIndex<playlist.length-1&&playAt(currentIndex+1)}><Text style={s.ctrl}>⏭</Text></TouchableOpacity>
        </View>
        <Text style={s.label}>Speed</Text>
        <View style={s.row}>
          {[0.5,0.75,1.0,1.25,1.5,2.0].map(sp=>(
            <TouchableOpacity key={sp} onPress={()=>changeSpeed(sp)} style={[s.chip,speed===sp&&s.on]}>
              <Text style={s.chipTxt}>{sp}x</Text>
            </TouchableOpacity>
          ))}
        </View>
        <Text style={s.label}>Volume</Text>
        <View style={s.row}>
          {[0.25,0.5,0.75,1.0].map(v=>(
            <TouchableOpacity key={v} onPress={()=>setVolume(v)} style={[s.chip,volume===v&&s.on]}>
              <Text style={s.chipTxt}>{Math.round(v*100)}%</Text>
            </TouchableOpacity>
          ))}
        </View>
        <TouchableOpacity style={s.addBtn} onPress={pickVideo}><Text style={s.addTxt}>+ Video Add</Text></TouchableOpacity>
        <ScrollView style={s.list}>
          {playlist.map((f,i)=>(
            <TouchableOpacity key={i} onPress={()=>playAt(i)} style={[s.item,i===currentIndex&&s.itemOn]}>
              <Text style={s.itemTxt} numberOfLines={1}>{f.name}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </>}
    </View>
  );
}

const s = StyleSheet.create({
  bg:{flex:1,backgroundColor:'#0a0a0a',alignItems:'center',paddingTop:40},
  title:{color:'#FF6B00',fontSize:24,fontWeight:'bold',marginBottom:12},
  video:{width,height:220,backgroundColor:'#000'},
  box:{width:width-40,height:180,backgroundColor:'#1a1a1a',borderRadius:14,justifyContent:'center',alignItems:'center',borderWidth:2,borderColor:'#FF6B00',borderStyle:'dashed'},
  boxIcon:{fontSize:48},
  boxTxt:{color:'#FF6B00',fontSize:15,marginTop:8},
  time:{color:'#888',fontSize:12,marginTop:8},
  bar:{width:width-40,height:4,backgroundColor:'#333',borderRadius:2,marginTop:6},
  fill:{height:4,backgroundColor:'#FF6B00',borderRadius:2},
  controls:{flexDirection:'row',alignItems:'center',gap:28,marginTop:14},
  ctrl:{fontSize:30,color:'#fff'},
  playBtn:{backgroundColor:'#FF6B00',width:64,height:64,borderRadius:32,justifyContent:'center',alignItems:'center'},
  playTxt:{fontSize:26,color:'#fff'},
  label:{color:'#FF6B00',fontSize:13,alignSelf:'flex-start',marginLeft:20,marginTop:12},
  row:{flexDirection:'row',flexWrap:'wrap',gap:8,marginLeft:20,marginTop:6},
  chip:{backgroundColor:'#1a1a1a',paddingHorizontal:12,paddingVertical:6,borderRadius:8,borderWidth:1,borderColor:'#333'},
  on:{borderColor:'#FF6B00',backgroundColor:'#2a1500'},
  chipTxt:{color:'#fff',fontSize:13},
  addBtn:{marginTop:12,backgroundColor:'#1a1a1a',padding:10,borderRadius:8,borderWidth:1,borderColor:'#FF6B00'},
  addTxt:{color:'#FF6B00',fontSize:13},
  list:{width:width-40,marginTop:10,maxHeight:140},
  item:{padding:10,backgroundColor:'#1a1a1a',marginBottom:6,borderRadius:8},
  itemOn:{backgroundColor:'#2a1500',borderWidth:1,borderColor:'#FF6B00'},
  itemTxt:{color:'#fff',fontSize:13},
});
