import React from "react";
import { Link } from "react-router-dom";
import { Grid, ButtonGroup, Button, Typography } from "@material-ui/core";

function Home() {
  return (
    <Grid container spacing={3} align="center">
    <Grid item xs={12}>
      <Typography variant="h3" component="h3">
        House Party
      </Typography>
    </Grid>
    <Grid item xs={12}>
      <ButtonGroup disableElevation variant="contained" color="primary">
        <Button color="primary" to="/join" component={Link}>
          Join a Room
        </Button>
        <Button color="secondary" to="/create" component={Link}>
          Create a Room
        </Button>
      </ButtonGroup>
    </Grid>
  </Grid>
  );
}

export default Home;