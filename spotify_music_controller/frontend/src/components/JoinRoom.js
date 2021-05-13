import React, { useState } from "react";
import { Grid, Button, Typography, TextField } from "@material-ui/core";
import { Link } from "react-router-dom";

function JoinRoom(props) {
  const [state, setState] = useState({
    code: "", 
    error: "",
  })

  const handleTextChange = (event) => {
    setState( 
      (prevState) => {
      return { ...prevState, code: event.target.value }
      }
    )
  }

  const handleJoinRoomClick = async () => {
    const request = {
      method: 'POST', 
      headers: { 'Content-Type': 'application/JSON' },
      body: JSON.stringify({ code: state.code })
    }
    const response = await fetch('/api/join-room/', request);
    const data = await response.json();
    
    try {
      if (response.ok) {
        props.history.push("/room/" + data.code)
      } else {
        setState((prevState) => {
          return { ...prevState, error: `${data.error}` } 
        })
      }
    } catch (error) {
      console.log(error)
    }
  }

  return (
    <Grid container spacing={1} align="center">

      {/* Join a Room field */}
      <Grid item xs={12}>
        <Typography variant="h4" component="h4">
          Join a Room
        </Typography>
      </Grid>

      <Grid item xs={12}>
        <TextField error={state.error} label="Code" onChange={handleTextChange} placeholder="Enter a code" value={state.code} helperText={state.error} variant="outlined" />
      </Grid>

      <Grid item xs={12}>
        <Button variant="contained" color="primary" onClick={handleJoinRoomClick}>Join Room</Button>
      </Grid>

      <Grid item xs={12}>
        <Button variant="contained" color="secondary" to="/" component={ Link }>Back</Button>
      </Grid>

    </Grid>
  )
}

export default JoinRoom;