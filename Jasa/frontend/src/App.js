import {Button, Checkbox, message} from "antd"
import { useEffect, useRef, useState } from "react";
import {genericFetch} from "./commands"
import VideoStream from "./VideoStream";
import BottomBar from "./BottomBar";
import "./App.css"
import TopBar from "./TopBar";

function App() {
  const [authUrl, setAuthUrl] = useState('');
  const [data, setData] = useState('');
  const [deviceState, setDeviceState] = useState(null)
  const stateRefresherIdRef = useRef(null);
  const timeIncreaserIdRef = useRef(null);

  const [doStateUpdates, setDoStateUpdates] = useState(false)
  const [emojiResponse, setEmojiResponse] = useState("")


  useEffect(()=>{
    if(sessionStorage["accessToken"]){

      // console.log("token changed to len" , sessionStorage["accessToken"].length)
    }
    // console.log("no token")
  },[sessionStorage["accessToken"]])


  useEffect(() => {
    //todo make this so it triggers when a post request is sent 
    getPlaybackState();

    // If the interval is already set, do nothing
    if (stateRefresherIdRef.current) return;
    const stateUpdatesFunc = ()=>{
      if(!doStateUpdates){
        // console.log(" skipping updating state " , doStateUpdates);
        return
      }
      // console.log("updating state");
      getPlaybackState();
    }

    // Set up the interval
    const id = setInterval(stateUpdatesFunc, 5000);

    // Store the interval ID in the re  f
    stateRefresherIdRef.current = id;

    // Cleanup function to clear the interval
    return () => {
      if (stateRefresherIdRef.current) {
        clearInterval(stateRefresherIdRef.current);
        stateRefresherIdRef.current = null;
      }
    };
  }, [doStateUpdates]);



  const getPlaybackState= ()=>{
    // console.log("getting playback state")
    const url="/getState"
    const body = {"token":sessionStorage["accessToken"]}
    const method = "POST"
    const headers = {'Content-Type': 'application/json'}
    fetch(url, {
      method: method,
      headers: headers,
      body: JSON.stringify(body) 
    }).then(response => {
      // console.log("response" ,response)
      return response.text()
      }).then(text=>{
        // console.log("text ",  text, text.body)
        const body = JSON.parse(text)
        // console.log("text", body.message)
        // console.log(body)
        setDeviceState(body)
      }).catch(err => {
        console.error("Error fetching data:", err); 

      })
  }
  const checkBoxClick= (e) => {
    console.log(`checked = ${e.target.checked}`);
    setDoStateUpdates(e.target.checked)
  };
  useEffect(()=>{
    console.log(deviceState)
  },[deviceState])
  return (
    <>
      <TopBar setData={setData}></TopBar>
      <div style={{
        margin:"5px",
      }}>
      <div>
        Do state updates:
        <Checkbox onChange={checkBoxClick} checked={doStateUpdates}></Checkbox>
          <div style={{
            color:"white"
          }}>
            response: {data}
          </div>
          <div style={{
            fontSize:"30px",
            height:"50px"
          }} >
            {emojiResponse}
          </div>
          <div></div>
          <VideoStream 
          setData={setData}
          deviceState={deviceState}
          setDeviceState={setDeviceState}
          emojiResponse={emojiResponse}
          setEmojiResponse={setEmojiResponse}
          ></VideoStream>
          </div>
      </div>
      <BottomBar setData={setData} deviceState={deviceState} setDeviceState={setDeviceState} playing=""></BottomBar>
      
    </>
  );
}

export default App;
