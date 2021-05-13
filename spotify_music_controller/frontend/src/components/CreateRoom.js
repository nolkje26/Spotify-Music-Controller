import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Button, Grid, Typography, TextField, FormHelperText, Radio, RadioGroup, FormControl, FormControlLabel } from "@material-ui/core";
import { Collapse } from "@material-ui/core";
import Alert from "@material-ui/lab/Alert";

function CreateRoom(props) {

  const [state, setState] = useState({
    guestCanPause: props.guestCanPause,
    votesToSkip: props.votesToSkip,
    code: props.code,
    errorMsg: "",
    successMsg: ""
  })

  const handleVotesChanged = (event) => {
    setState( 
      (prevState) => {
      return { ...prevState, votesToSkip: event.target.value }
      }
    )
  }

  const handleGuestCanPauseChange = (event) => {
    setState( 
      (prevState) => {
      return { ...prevState, guestCanPause: event.target.value === 'true' ? true : false }
      }
    )
  }

  const handleCreateRoomButtonClicked = async () => {
    const request = {
      method: 'POST', 
      headers: { 'Content-Type': 'application/JSON' },
      body: JSON.stringify({
        guest_can_pause: state.guestCanPause,
        votes_to_skip: state.votesToSkip
      })
    };
    // fetch('/api/create-room/', request)
    // .then((response) => response.json())
    // .then((data) => console.log(data));

    let response = await fetch('/api/create-room/', request)
    let data = await response.json()
    props.history.push("/room/" + data.code) // This will redirect you to newly created room
  }

  const handleUpdateButtonClicked = async () => {
    const request = {
      method: 'PATCH',
      headers: {'Content-Type': 'application/JSON'},
      body: JSON.stringify({
        guest_can_pause: state.guestCanPause,
        votes_to_skip: state.votesToSkip, 
        code: state.code,
      })
    }

    let response = await fetch('/api/update-room/', request)
    
    if (response.ok) {
      setState( 
        prevState => {
        return {...prevState, successMsg: "Room updated"}
        })
    } else {
        setState( 
          prevState => {
          return {...prevState, errMsg: "Error"}
          })
    }
      props.updateCallback();
  }

  const renderCreateAndBackButton = () => {
    return(
      <Grid container spacing={1} align="center">
        <Grid item xs={12} align="center">
          <Button color="primary" variant="contained" onClick={handleCreateRoomButtonClicked}>Create Room</Button>
        </Grid>
        <Grid item xs={12} align="center">
          <Button color="secondary" variant="contained" to="/" component={Link}>Back</Button>
        </Grid>
      </Grid>
    )
  }

  const renderUpdateAndCloseButton = () => {
    return(
      <Grid item xs={12} align="center">
        <Button color="primary" variant="contained" onClick={handleUpdateButtonClicked}>Update Room</Button>
      </Grid>
    )
  }


  const title = props.updateMode ? "Update Room" : "Create Room";

  return (
    <Grid container spacing={1} align="center">
      <Grid item xs={12}>
          <Collapse 
            in={state.errorMsg != "" || state.successMsg != ""}>
            {state.successMsg == "" ? 
            (<Alert
              severity="error"
              onClose={() => {
                setState(prevState => {
                return setState({ ...prevState, successMsg: "" })})}}>
                {state.errorMsg}
            </Alert>) : 
            (<Alert 
              severity="success" 
              onClose={() => {
                setState(prevState => {
                return setState({ ...prevState, successMsg: "" })})}}>
                {state.successMsg}
            </Alert>)}
          </Collapse>
      </Grid>

      {/* Create a room  */}
      <Grid item xs={12} >
        <Typography componen="h4" varient="h4">{title}</Typography>
      </Grid>

      {/* Radio Buttons */}
      <Grid item xs={12} >
        <FormControl component="fieldset">
          <FormHelperText>
            <div >Guest Control of Playback State</div>
          </FormHelperText>
          <RadioGroup row defaultValue="false" onClick={handleGuestCanPauseChange}>
            <FormControlLabel value="true" control={<Radio color="primary"/>} label="Play/Pause" labelPlacement="bottom"/>
            <FormControlLabel value="false" control={<Radio color="secondary"/>} label="No Control" labelPlacement="bottom"/>
          </RadioGroup>
        </FormControl>
      </Grid>

    {/* Votes to skip */}
      <Grid item xs={12} >
        <FormControl>
          <TextField required={true} type="number" onClick={handleVotesChanged} defaultValue={state.votesToSkip} inputProps={{min: 1, style: {textAlign: "center"}}}/>
          <FormHelperText>
            <div >Votes required to skip song</div>
          </FormHelperText>
        </FormControl>
      </Grid>

    {/* Buttons: Create Room/Back  */}
    {props.updateMode ? renderUpdateAndCloseButton() : renderCreateAndBackButton()}


    </Grid>
  );
}

CreateRoom.defaultProps = {
  guestCanPause: false, 
  votesToSkip: 2,
  code: null, 
  updateMode: false, 
  updateCallback: () => {}, 
};

export default CreateRoom;