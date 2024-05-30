
const pauseMusic= ()=>{
    console.log("pausing")
    const url = '/pause'
    return genericFetch(url)
  }

  const continueMusic= ()=>{
    console.log("continuing")
    const url = '/continuePlaying'
    return genericFetch(url)
    
  }
  const nextSong= ()=>{
    console.log("going to next song")
    const url = '/nextSong'
    return genericFetch(url)
    
  }
  const prevSong= ()=>{
    console.log("going to prev song")
    const url = '/prevSong'
    return genericFetch(url)
    
  }
  const volumeUp = ()=>{
    console.log("increasing volume")
    const url = '/volumeUp'
    return genericFetch(url)
    
  }
  const volumeDown= ()=>{
    console.log("decreasing volume")
    const url = '/volumeDown'
    return genericFetch(url)
    
  }

  const genericFetch = (url,
    body = {"token":sessionStorage["accessToken"]},
    method = "POST",
    headers = {'Content-Type': 'application/json'}
  )=>{
    return  fetch(url, {
      method: method,
      headers: headers,
      body: JSON.stringify(body) 
    })
    .then(response => {
      // console.log("response" ,response)
      return response.text()
      }).then(text=>{
        // console.log("text ",  text, text.body)
        const body = JSON.parse(text)
        // console.log("text", body.message)
        return {
          message:body.message
        }
      })
      .catch(err => {
        console.error("Error fetching data:", err); 
        return {
            success:false,
            message:"Error fetching data:"+ err
        }
    });
  }

  module.exports = { pauseMusic, continueMusic,nextSong, prevSong, volumeUp, volumeDown , genericFetch};

