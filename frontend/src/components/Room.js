import React, { Component } from 'react';
import { Grid, Button, Typography } from '@material-ui/core';
import CreateRoomPage from './CreateRoomPage';
import MusicPlayer from './MusicPlayer';


export default class Room extends Component {
    constructor(props) {
        super(props);
        this.state = {
            votesToSkip: 2,
            guestCanPause: false,
            isHost: false,
            showSettings: false,
            spotifyAuthenticated: false,
            // Storing all information about current song in the state of this component
            song: {}
        };
        // Match is added by router (its what was used to get to this page)
        this.roomCode = this.props.match.params.roomCode;
        this.leaveButtonPressed = this.leaveButtonPressed.bind(this);
        this.updateShowSettings = this.updateShowSettings.bind(this);
        this.renderSettingsButton = this.renderSettingsButton.bind(this);
        this.renderSettings = this.renderSettings.bind(this);
        this.getRoomDetails = this.getRoomDetails.bind(this);
        this.authenticateSpotify = this.authenticateSpotify.bind(this);
        this.getCurrentSong = this.getCurrentSong.bind(this);
        this.getRoomDetails();
    }

    // Lifecycle method (called once component has been loaded on screen)
    componentDidMount() {
        // Call getCurrentSong method every second
        // This is called a pulling method and it is suboptimal
        //   since for large numbers of users we would be making too many requests
        // but since spotify api does not support web sockets this is the next best thing
        this.interval = setInterval(this.getCurrentSong, 1000);
    }

    // Lifecycle method (called once component is about to be cleared)
    componentWillUnmount() {
        clearInterval(this.interval);
    }

    getRoomDetails () {
        fetch('/api/get-room' + '?code=' + this.roomCode)
            .then((response) => {
                if (!response.ok) {
                    this.props.leaveRoomCallback();
                    this.props.history.push("/");
                }
                return response.json();
            })
            .then((data) => {
                this.setState({
                    votesToSkip: data.votes_to_skip,
                    guestCanPause: data.guest_can_pause,
                    isHost: data.is_host, 
                });
                if (this.state.isHost) {
                    this.authenticateSpotify();  
                }
            });
    }

    authenticateSpotify() {
        fetch("/spotify/is-authenticated")
          .then((response) => response.json())
          .then((data) => {
            console.log(data);
            this.setState({ spotifyAuthenticated: data.status });
            //console.log(data.status);
            if (!data.status) {
              fetch("/spotify/get-auth-url")
                .then((response) => response.json())
                .then((data) => {
                  // Native Js way of redirecting
                  window.location.replace(data.url);
                });
            }
          });
      }

      getCurrentSong() {
          fetch('/spotify/current-song')
            .then((response) => {
                if (!response.ok) {
                    return {};
                } else {
                    return response.json();
                }
            })
            .then((data) => {
                this.setState({song: data});
                console.log(data);
            });
      }

    leaveButtonPressed() {
        const requestOptions = {
            method: "POST",
            headers: {'Content-Type': "application/json"},
        };
        fetch('/api/leave-room', requestOptions).then((_response) => {
            this.props.leaveRoomCallback();
            this.props.history.push("/");
        });
    }

    updateShowSettings(value) {
        this.setState({
            showSettings: value,
        });
    }

    renderSettings() {
        return (
            <Grid container spacing={1}>
                <Grid item xs={12}>
                    <CreateRoomPage 
                        update={true}
                        votesToSkip={this.state.votesToSkip}
                        guestCanPause={this.state.guestCanPause}
                        roomCode={this.roomCode}
                        updateCallback={this.getRoomDetails}
                    />
                </Grid>
                <Grid item xs={12} align="center">
                    <Button
                        variant="contained"
                        color="secondary"
                        align="center"
                        onClick={() => this.updateShowSettings(false)}
                    >
                        Close
                    </Button>
                </Grid>
            </Grid>
        );
    }

    renderSettingsButton() {
        return (
            <Grid item xs={12} align="center">
                <Button 
                    variant="contained" 
                    color="primary"
                    onClick={() => this.updateShowSettings(true)}
                >
                    Settings
                </Button>
            </Grid>
        );
    }

    // ...this.state.song is using the spread operator '...'
    // to pass each value in song as a separate prop to MusicPlayer
    render() {
        if (this.state.showSettings) {
            return this.renderSettings();
        }
        return (
            <Grid container spacing={2}>
                <Grid item xs={12} align="center">
                    <Typography variant="h4" component="h4">
                        Code: {this.roomCode}
                    </Typography>
                </Grid>
                <MusicPlayer {...this.state.song} />
                {this.state.isHost ? this.renderSettingsButton() : null}
                <Grid item xs={12} align="center">    
                    <Button
                        variant="contained"
                        color="secondary"
                        onClick={ this.leaveButtonPressed }
                    >
                        Leave Room
                    </Button>
                </Grid>
            </Grid>
        );
    }
}
