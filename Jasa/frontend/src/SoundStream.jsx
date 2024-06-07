import React, { useState, useEffect } from 'react';
import { FFmpeg } from '@ffmpeg/ffmpeg'

import ReactDOM from "react-dom/client";
import { AudioRecorder } from 'react-audio-voice-recorder';

const MicrophoneCapture = () => {
  const [isRecording, setIsRecording] = useState(false);

  const downloadBlob = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  const ffmpeg = new FFmpeg({ log: true });
  const uploadAudio = async (blob) => {
      
      
      if (!ffmpeg.loaded) {
          await ffmpeg.load();
        }
        
        const inputName = 'input.webm';
        const outputName = 'output.wav';
        
        // Convert the Blob to an ArrayBuffer
        const arrayBuffer = await blob.arrayBuffer();
        
        // Write the ArrayBuffer to the ffmpeg filesystem
        await ffmpeg.writeFile(inputName, new Uint8Array(arrayBuffer));
        
        // Run the conversion from webm to wav
        await ffmpeg.exec(['-i', inputName, outputName]);
        
        // Read the resulting wav file
        const outputData = await ffmpeg.readFile(outputName);
        const outputBlob = new Blob([outputData.buffer], { type: 'audio/wav' });
        
        
        // downloadBlob(outputBlob,"recording.wav")
        const formData = new FormData();
        formData.append('file', outputBlob, 'recording.wav');
        fetch('/uploadSound', {
            method: 'POST',
            body:formData
        })
        .then(response => response.json())
        .then(data => {
        console.log('Success:', data); 
      })
      .catch(error => {
        console.error('Error:', error);
      });
  };
  const executeSignCommand = (sign)=>{
    if(recentRef.current)return
    //pauseMusic, continueMusic, volumeDown, volumeUp, nextSong, prevSong
    //functions that can be called
    switch(sign){
      case("fist"):
            console.log("recieved fist")
            volumeDown()
            props.setEmojiResponse("👊-volume down")
            break
            
            case("hand"):
            console.log("recieved hand")
            volumeUp()
            props.setEmojiResponse("✋-volume up")
            break
            case("thumbs up"):
            console.log("recieved thumbs up")
            nextSong()
            props.setEmojiResponse("👍-pause")

            break
            case("peace"):
            console.log("recieved peace sign")
            //toggle
            

            if(props.deviceState?.is_playing){
              pauseMusic()
              props.setEmojiResponse("✌️-toggle music->pause")
              props.setDeviceState(a => {
                if(a?.is_playing === true){
                  
                  a.is_playing = false
                }
                return a
              })
            }else{
              continueMusic()
              props.setEmojiResponse("✌️-toggle music->continue")
              props.setDeviceState(a => {
                if(a?.is_playing === false){
                  
                  a.is_playing = true
                }
                return a
              })
            }
            break
      default:
        console.log("recieved alternate ", sign)
    }
  }
  return (
    <div>
    {typeof SharedArrayBuffer !== 'undefined'?"cors works":"cors doesnt work"}
      <AudioRecorder 
      onRecordingComplete={uploadAudio}
      audioTrackConstraints={{
        noiseSuppression: true,
        echoCancellation: true,
      }} 
      downloadFileExtension="wav"
    //   downloadOnSavePress={true}
    />
    </div>
  );
};

export default MicrophoneCapture;
