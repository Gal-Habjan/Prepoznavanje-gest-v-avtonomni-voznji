import { Button } from "antd"
import "./TopBar.css"
import { useEffect } from "react";
var Url = require('url-parse');
const TopBar = ({setData})=>{

    useEffect(()=>{
        const queryParams = new URLSearchParams(window.location.search);
        const params = {};
        // console.log("queryParams " , queryParams)
        queryParams.forEach((value, key) => {
          params[key] = value;
        });
    
        // console.log("queryParams ", params)
        if(params.code){
    
          sessionStorage.setItem('accessToken', params.code);
          // console.log("sucesfull login, key:",params.code, params)
          setData("logged in sucesfully")
        }
        },[])
    const buttonStyle = {
        backgroundColor:"#04AA6D",
        borderColor:"#04AA6D",
        height:"fit-content",
        // width:"200px",
        margin:"5px",
        top:"10px",
        // justifyContent:"center",
        fontSize:"25px",

    }

    return (
    <div style={{
        height: "80px",
        background:"#162028", 
        margin:"0px",
        top:"0%",
        left:"0px",
        width:"100%", 
        margin:"0px",
        display:"flex",
        justifyContent:"left"
    }}>
        <Button  style={buttonStyle}
            href="http://127.0.0.1:5000/loginReact">
                {sessionStorage["accessToken"]?"logged in":"log in to spotify"}
        </Button>

    </div>)
}
export default TopBar