// MusicPlayer.js
import React, { Component } from "react";
import {
    Grid,
    Typography,
    Card,
    IconButton,
    LinearProgress,
} from "@material-ui/core";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";
import PauseIcon from "@material-ui/icons/Pause";
import SkipNextIcon from "@material-ui/icons/SkipNext";

export default class MusicPlayer extends Component {
    constructor(props) {
        super(props);
    }

    static defaultProps = {
        image_url: "",
        title: "未知歌曲",
        artist: "未知艺术家",
        is_playing: false,
        time: 0,
        duration: 1,
        isHost: false  // 默认非 host
    };

    skipSong() {
        fetch("/spotify/skip", { method: "POST" })
            .then((response) => {
                if (response.status === 403) {
                    alert("Only the host can skip the song!");
                } else if (response.status === 400) {
                    response.json().then(data => {
                        alert("Error: " + (data.Error || "Unknown error"));
                    });
                } else if (response.status === 204) {
                    console.log("Song skipped successfully");
                }
            })
            .catch((error) => {
                console.error("Network error:", error);
            });
    }

    pauseSong() {
        const requestOptions = {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
        };
        fetch("/spotify/pause", requestOptions);
    }

    playSong() {
        const requestOptions = {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
        };
        fetch("/spotify/play", requestOptions);
    }

    render() {
        const songProgress = (this.props.time / this.props.duration) * 100;

        return (
            <Card>
                <Grid container alignItems="center">
                    <Grid item align="center" xs={4}>
                        <img src={this.props.image_url} height="100%" width="100%" />
                    </Grid>
                    <Grid item align="center" xs={8}>
                        <Typography component="h5" variant="h5">
                            {this.props.title}
                        </Typography>
                        <Typography color="textSecondary" variant="subtitle1">
                            {this.props.artist}
                        </Typography>
                        <div>
                            <IconButton onClick={() => {
                                this.props.is_playing ? this.pauseSong() : this.playSong();
                            }}>
                                {this.props.is_playing ? <PauseIcon /> : <PlayArrowIcon />}
                            </IconButton>
                            <IconButton onClick={() => this.skipSong()}>
                                <SkipNextIcon />
                            </IconButton>
                        </div>
                    </Grid>
                </Grid>
                <LinearProgress variant="determinate" value={songProgress} />
            </Card>
        );
    }
}