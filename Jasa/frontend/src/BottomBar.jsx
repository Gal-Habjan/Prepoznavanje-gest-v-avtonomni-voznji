import { Button, Progress } from "antd";
import { useEffect, useState } from "react";
import {pauseMusic, continueMusic, nextSong, prevSong, volumeUp, volumeDown} from "./commands"
import "./BottomBar.css"

const BottomBar = ({setData, deviceState, setDeviceState})=>{
    const [timeIncreaserId , setTImeIncreaserId] = useState(null)

    

    const pauseMusicButton = async ()=>{
        const response = await pauseMusic()
        console.log("pause message: ", response.message)
        setData(response.message)
        setDeviceState(a => {
          if(a?.is_playing === true){

            a.is_playing = false
          }
          return a
        })
      }
      const continueMusicButton = async ()=>{
        const response = await continueMusic()
        console.log("continue message: ", response.message)
        setData(response.message)
        setDeviceState(a => {
          if(a?.is_playing === false){

            a.is_playing = true
          }
          return a
        })
      }
      const nextSongButton = async ()=>{
        const response = await nextSong()
        console.log("next song message: ", response.message)
        setData(response.message)
      }
      const prevSongButton = async ()=>{
        const response = await prevSong()
        console.log("prev song message: ", response.message)
        setData(response.message)
      }
      const volumeUpButton = async ()=>{
        const response = await volumeUp()
        console.log("volumeUp message: ", response.message)
        setData(response.message)
      }
      const volumeDownButton = async ()=>{
        const response = await volumeDown()
        console.log("volumeDown message: ", response.message)
        setData(response.message)
      }
    
    const buttonStyle = {
        backgroundColor:"#04AA6D",
        borderColor:"#04AA6D",
        height:"70%",
        width:"200px",
        margin:"5px",
        top:"10px",
        fontSize:"25px",
        fontFamily:"Arial",
        color:"red"
    }

    return (
    <>

    {deviceState?
    <>
    <div>{deviceState?.item?.name}</div>
    <Progress key={deviceState} percent={deviceState.progress_ms/deviceState?.item?.duration_ms*100}></Progress>
    </>
    :""}
    <div style={{
        height: "80px",
        background:"#162028", 
        position: "fixed", 
        margin:"0px",
        bottom:"0%",
        overflow:"hidden",
        left:"0px",
        width:"100%", 
        display:"flex",

    }}>
      {deviceState?.is_playing?
      <Button onClick={()=>pauseMusicButton()} style={buttonStyle}>⏹️</Button>
      :
      <Button onClick={()=>continueMusicButton()}style={buttonStyle}>▶️</Button>
    }
        <Button onClick={()=>prevSongButton()}style={buttonStyle}>⏮️</Button>
        <Button onClick={()=>nextSongButton()}style={buttonStyle}>⏭️</Button>
        <Button onClick={()=>volumeUpButton()}style={buttonStyle}>🔊</Button>
        <Button onClick={()=>volumeDownButton()}style={buttonStyle}>🔉</Button>
        </div>

    </>
    )

}

export default BottomBar