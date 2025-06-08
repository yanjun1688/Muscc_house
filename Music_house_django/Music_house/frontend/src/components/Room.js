import React, { Component } from "react";
import { Grid, Button, Typography } from "@material-ui/core";
import CreateRoomPage from "./CreateRoomPage";
import MusicPlayer from "./MusicPlayer";

export default class Room extends Component {
    constructor(props) {
        super(props);
        this.state = {
            votesToSkip: 2,
            guestCanPause: false,
            isHost: false,
            showSettings: false,
            spotifyAuthenticated: false,
            song: {},
        };

        this.roomCode = this.props.match?.params?.roomCode || "";
        console.log("Room code from props:", this.roomCode);

        this.leaveButtonPressed = this.leaveButtonPressed.bind(this);
        this.updateShowSettings = this.updateShowSettings.bind(this);
        this.renderSettingsButton = this.renderSettingsButton.bind(this);
        this.renderSettings = this.renderSettings.bind(this);
        this.getRoomDetails = this.getRoomDetails.bind(this);
        this.authenticatedSpotify = this.authenticatedSpotify.bind(this);
        this.getCurrentSong = this.getCurrentSong.bind(this);
        this.getRoomDetails();
    }

    componentDidMount() {
        this.interval = setInterval(this.getCurrentSong, 10000);
    }

    componentWillUnmount() {
        clearInterval(this.interval);
    }

    getRoomDetails() {
        fetch("/api/get-room" + "?code=" + this.roomCode)
            .then((response) => {
                if (!response.ok) {
                    this.props.leaveRoomCallback();
                    this.props.history.push("/");
                }
                return response.json();
            })
            .then((data) => {
                console.log("Data received from API:", data);
                this.setState(
                    {
                        votesToSkip: data.votes_to_skip,
                        guestCanPause: data.guest_can_pause,
                        isHost: data.is_host,
                    },
                    () => {
                        if (this.state.isHost) {
                            this.authenticatedSpotify();
                        }
                    }
                );
            })
            .catch((error) => console.error("Error fetching room details:", error));
    }

    authenticatedSpotify() {
        fetch("/spotify/is-authenticated")
            .then((response) => response.json())
            .then((data) => {
                this.setState({ spotifyAuthenticated: data.status });
                if (!data.status) {
                    fetch("/spotify/get-auth-url")
                        .then((response) => response.json())
                        .then((data) => {
                            window.location.replace(data.url);
                        })
                        .catch((error) =>
                            console.error("Error fetching auth URL:", error)
                        );
                }
            })
            .catch((error) =>
                console.error("Error checking Spotify authentication:", error)
            );
    }

    getCurrentSong() {
        fetch("/spotify/current-song")
            .then((response) => {
                if (!response.ok) {
                    return {};
                }
                return response.json();
            })
            .then((data) => {
                console.log("Spotify data received:", data);
                if (
                    data &&
                    Object.keys(data).length > 0 &&
                    JSON.stringify(data) !== JSON.stringify(this.state.song)
                ) {
                    this.setState({ song: data });
                }
            })
            .catch((error) => console.error("Error fetching song:", error));
    }

    leaveButtonPressed() {
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        };
        fetch("/api/leave-room", requestOptions).then((_response) => {
            this.props.leaveRoomCallback();
            this.props.history.push("/");
        });
    }

    updateShowSettings(value) {
        this.setState({ showSettings: value });
    }

    renderSettings() {
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
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
                        onClick={() => this.updateShowSettings(false)}
                    >
                        关闭房间
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

    render() {
        if (this.state.showSettings) {
            return this.renderSettings();
        }
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Typography variant="h4" component="h4">
                        Code: {this.roomCode}
                    </Typography>
                </Grid>
                {this.state.song && Object.keys(this.state.song).length > 0 ? (
                    //   <MusicPlayer {...this.state.song} />
                    // 这里要处理下数据结构，否则会有问题。
                    <MusicPlayer
                        image_url={this.state.song.item?.album?.images[0]?.url || ""}
                        title={this.state.song.item?.name || ""}
                        artist={this.state.song.item?.artists[0]?.name || ""}
                        is_playing={this.state.song.is_playing || false}
                        time={this.state.song.progress_ms || 0}
                        duration={this.state.song.item?.duration_ms || 1}
                        isHost ={this.state.isHost}
                    />
                ) : (
                    <Typography variant="h6">No song data available</Typography>
                )}
                <Grid item xs={12} align="center">
                    <Typography variant="h6" component="h6">
                        {this.state.song.name
                            ? `Currently playing: ${this.state.song.name}`
                            : "No song is currently playing"}
                    </Typography>
                </Grid>
                {this.state.isHost ? this.renderSettingsButton() : null}
                <Grid item xs={12} align="center">
                    <Button
                        variant="contained"
                        color="secondary"
                        onClick={this.leaveButtonPressed}
                    >
                        Leave Room
                    </Button>
                </Grid>
            </Grid>
        );
    }
}