import React, { useState, useEffect } from "react";
import { Grid, Button, Typography } from "@material-ui/core";
import CreateRoom from "./CreateRoom"

function Room(props) {
    const defaultVotes = 2;

    const [state, setState] = useState({
        guestCanPause: false, 
        votesToSkip: defaultVotes,
        isHost: false,
        showSettings: false,
        isSpotifyAuthenticated: false
    })

    const code = props.match.params.code;

    const getRoom = async () => {
        const response = await fetch('/api/get-room?code=' + code);
        const data = await response.json();
        setState((prevState) => (
            {...prevState,
                guestCanPause: data.guest_can_pause,
                votesToSkip: data.votes_to_skip,
                isHost: data.is_host
            }
        ))
    }
    
    const authenticateSpotify = async () => {
        const response = await fetch("/spotify/is-authenticated");
        const data = await response.json()
        setState((prevState) => (
            {...prevState,
            isSpotifyAuthenticated: data.status
        }))

        if (!data.status) {
            const url_resp = await fetch("/spotify/get-auth-url")
            const url_data = await url_resp.json()
            window.location.replace(url_data.url)
        }
    }

    const updateShowSettings = (boolVal) => {
        setState(prevState => {
            return {
                ...prevState,
                showSettings: boolVal
            }
        })
    }

    const renderSettingsButton = () => {
        return (
            <Grid item xs={12}>
                <Button variant="contained" color="primary" onClick={() => updateShowSettings(true)}>
                    Settings
                </Button>
            </Grid>
        )
    }

    const renderSettings = () => {
        return (
            <Grid container spacing={1} align="center">
                <Grid item xs={12}>
                    <CreateRoom updateMode={true} votesToSkip={state.votesToSkip} guestCanPause={state.guestCanPause} code={code} updateCallback={getRoom} />
                </Grid>
                <Grid item xs={12}>
                    <Button variant="contained" color="secondary" onClick={() => updateShowSettings(false)}>
                        Close
                    </Button>
                </Grid>
            </Grid>
        )
    }
    
    const handleLeaveRoomButtonClicked = async () => {
        const request = {
            method: 'POST',
            headers: {'Content-Type' : 'application/json'}
        };

        await fetch('/api/leave-room/', request);
        props.history.push("/");
    }

    useEffect( () => {
        getRoom();
    }, []);

    useEffect( () => {
        if (state.isHost) {
            authenticateSpotify();
        }
    }, [state.isHost]);

    if (state.showSettings) {
        return renderSettings()
    }

    return (
        <Grid container spacing={1} align="center">
            <Grid item xs={12}>
                <Typography variant="h6" component="h6">
                    Code: {code}
                </Typography>
            </Grid>
            <Grid item xs={12}>
                <Typography variant="h6" component="h6">
                    Guest Can Pause: {state.guestCanPause.toString()}
                </Typography>
            </Grid>
            <Grid item xs={12}>
                <Typography variant="h6" component="h6">
                    Votes to Skip: {state.votesToSkip.toString()}
                </Typography>
            </Grid>
            <Grid item xs={12}>
                <Typography variant="h6" component="h6">
                    Host: {state.isHost.toString()}
                </Typography>
            </Grid>
            {state.isHost ? renderSettingsButton() : null}
            <Grid item xs={12}>
                <Button variant="contained" color="secondary" onClick={handleLeaveRoomButtonClicked}>
                    Leave Room
                </Button>
            </Grid>
        </Grid>
    );
}

export default Room;