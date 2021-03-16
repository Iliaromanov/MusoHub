import React, { Component } from "react";
import JoinRoomPage from "./JoinRoomPage";
import CreateRoomPage from "./CreateRoomPage";
import Room from "./Room";
import {
    BrowserRouter as Router, 
    Switch, 
    Route, 
    Link, 
    Redirect
} from "react-router-dom";

export default class HomePage extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        // Must use exact keyword in routes or else all similar routes will go to the same place
        return (
        <Router>
            <Switch>
                <Route exact path='/'><h1>MusoHub</h1></Route>
                <Route path='/join' component={JoinRoomPage} />
                <Route path='/create' component={CreateRoomPage} />
                <Route path="/room/:roomCode" component={Room} />
            </Switch>
        </Router>);
    }
}