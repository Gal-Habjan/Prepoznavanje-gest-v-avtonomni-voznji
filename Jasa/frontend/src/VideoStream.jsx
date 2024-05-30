import { Button } from "antd";
import { useState,useRef } from "react";
import {pauseMusic, continueMusic, volumeDown, volumeUp, nextSong, prevSong} from "./commands"
const VideoStream = (props)=>{
    const captureRate = 2 //how many times per second
    const commandDelay = 2000 //delay after a command is recognised before a new one can be sent
    

    const [streaming, setStreaming] = useState(false);
    const [streamHolder, setStreamHolder] = useState(null)
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const photoRef = useRef(null);

    const [isRecentCommand, setIsRecentCommand] = useState(false) //if a command was recognised inside the commandDelay window
    const [commandDelayIntervalId, setCommandDelayIntervalId] = useState(null)
    const [intervalId, setIntervalId] = useState(null)
    const recentRef = useRef(false)

    const startVideo = () => {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                setStreaming(true);
                let video = videoRef.current;
                video.srcObject = stream;
                setStreamHolder(stream)
                video.play();
                const id = setInterval(takePhoto,1000/captureRate)
                setIntervalId(id)

            })
            .catch(err => {
                console.error("Error accessing the camera: ", err);
            });
    };
    const stopVideo = () => {
        try{
            if(intervalId){
              clearInterval(intervalId)
              setIntervalId(null)
            }
            streamHolder.getTracks().forEach(function(track) {
              track.stop();
            });
            setStreaming(false);
        }
        catch(e){
            console.log("error closing stream ", e)
        }
    }
        
    // Capture a photo from the video stream
    const takePhoto = () => {
        if(recentRef.current)return
        const imageResolution = 1; //between 0 and 1, 1 is highest
        const video = videoRef.current;
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');
        const width = video.videoWidth;
        const height = video.videoHeight;
  
        canvas.width = width;
        canvas.height = height;
        context.drawImage(video, 0, 0, width, height);
  
        const imageDataUrl = canvas.toDataURL('image/jpeg',imageResolution).replace("image/jpeg", "image/octet-stream");
        // console.log("sending image")
        photoRef.current.src = imageDataUrl;
  
        
      fetch('/uploadImage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageDataUrl })
      })
      .then(response => {
        if(recentRef.current)return
        const res = response.json()  
        // console.log(response)
        return res
      })
      .then(data => {
        // console.log(data.sign)
        props.setData(data.sign)

        executeSignCommand(data.sign)
      
      })
        .catch(err => console.error("Error sending image:", err, ));
    };
    const executeSignCommand = (sign)=>{
      if(recentRef.current)return
      //pauseMusic, continueMusic, volumeDown, volumeUp, nextSong, prevSong
      //functions that can be called
      switch(sign){
        case("fist"):
              console.log("recieved fist")
              volumeDown()
              recentRef.current = (true)
              props.setEmojiResponse("👊")
              commandInterval()
              break
              
              case("hand"):
              console.log("recieved hand")
              volumeUp()
              recentRef.current = (true)
              props.setEmojiResponse("✋")
              commandInterval()
              break
              case("thumbs up"):
              console.log("recieved thumbs up")
              recentRef.current = (true)
              props.setEmojiResponse("👍")
              pauseMusic()
              props.setDeviceState(a => {
                if(a?.is_playing === true){
                  
                  a.is_playing = false
                }
                return a
              })
              commandInterval()
              break
              case("peace sign"):
              console.log("recieved peace sign")
              //toggle
              
              continueMusic()
              props.setDeviceState(a => {
                if(a?.is_playing === false){
                  
                  a.is_playing = true
                }
                return a
              })
              recentRef.current = (true)
              props.setEmojiResponse("✌️")
              commandInterval()
              break
        default:
          console.log("recieved alternate ", sign)
      }
    }

    const commandInterval = ()=>{
      setTimeout(()=>{
        recentRef.current = (false)
        props.setEmojiResponse("")
      },commandDelay)
    }
    return (<>
        <div>
          {!intervalId?
        <Button onClick={startVideo} disabled={streaming}>Start Camera</Button>
        :
        <Button onClick={stopVideo} disabled={!streaming}>StopCamera</Button>
      }
      {/* <Button onClick={takePhoto} disabled={!streaming}>Take Photo</Button> */}
        <div>
          {intervalId??"no interval"}
        </div>
        </div>
        <video ref={videoRef}></video>
        <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>
        <img style={{color:"gray"}}ref={photoRef} alt="No capture taken yet" />
    </>)
}
export default VideoStream