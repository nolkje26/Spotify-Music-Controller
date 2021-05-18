import React, { useState, useEffect } from 'react';
import Home from './Home';
import JoinRoom from './JoinRoom';
import CreateRoom from './CreateRoom';
import Room from './Room';
import { BrowserRouter as Router, Switch, Route, Redirect } from 'react-router-dom';


function App() {

  const [state, setState] = useState({ code : null });

  useEffect(async () => {
    const response = await fetch("/api/user-in-room");
    const data = await response.json();
    setState({ code: data.code });
  }, [state.code])

  return (
    <div className="center">
      <Router>
        <Switch>
          <Route exact path="/" render={() => {
                return state.code ? <Redirect to={`/room/${state.code}`} /> :  <Home /> }}/>
          <Route exact path="/" component={Home}/>
          <Route path="/join" component={JoinRoom} />
          <Route path="/create" component={CreateRoom} />
          <Route path="/room/:code" component={Room} />
        </Switch>
      </Router>
    </div>
  );
}

export default App