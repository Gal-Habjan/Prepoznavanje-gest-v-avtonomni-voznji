import React, { useState, useEffect } from 'react';

import ReactDOM from "react-dom/client";
import { AudioRecorder } from 'react-audio-voice-recorder';

const MicrophoneCapture = () => {
  const [isRecording, setIsRecording] = useState(false);


  const uploadAudio = (blob) => {
    const formData = new FormData();
    formData.append('file', blob, 'recording.webm');

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
  return (
    <div>
      <AudioRecorder 
      onRecordingComplete={uploadAudio}
      audioTrackConstraints={{
        noiseSuppression: true,
        echoCancellation: true,
      }} 
      downloadFileExtension="webm"
    />
    </div>
  );
};

export default MicrophoneCapture;
