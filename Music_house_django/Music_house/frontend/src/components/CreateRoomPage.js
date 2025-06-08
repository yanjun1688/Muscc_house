import React, { Component } from "react";
import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import { Link } from "react-router-dom";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import { Collapse } from "@material-ui/core";


export default class CreateRoomPage extends Component {
   static defaultProps = {
      votesToSkip: 2,
      guestCanPause: true,
      update: false,
      roomCode: null,
      updateCallback: () => { },
   }
   constructor(props) {
      super(props);
      this.state = {
         guestCanPause: this.props.guestCanPause,
         votesToSkip: this.props.votesToSkip,
         errosMsg: "",
         successMsg: '',
      };
      this.handleRoomButtonPressed = this.handleRoomButtonPressed.bind(this);
      this.handleVotesChanged = this.handleVotesChanged.bind(this);
      this.handleGuestCanPauseChanged = this.handleGuestCanPauseChanged.bind(this);
      this.handleUpdateButtonPressed = this.handleUpdateButtonPressed.bind(this);
   }
   handleVotesChanged(e) {
      this.setState({
         votesToSkip: e.target.value,
      });
   }
   handleGuestCanPauseChanged(e) {
      this.setState({
         guestCanPause: e.target.value === "true" ? true : false
      })
   }
   handleRoomButtonPressed() {
      console.log(this.state)
      const requestOptions = {
         method: "POST",
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({
            votes_to_skip: this.state.votesToSkip,
            guest_can_pause: this.state.guestCanPause
         }),
      };
      fetch('/api/create-room', requestOptions)
         .then((response) => response.json())
         .then((data) => this.props.history.push('room/' + data.code));
   }
   handleUpdateButtonPressed() {
      const requestOptions = {
         method: "PATCH",
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({
            votes_to_skip: this.state.votesToSkip,
            guest_can_pause: this.state.guestCanPause,
            code: this.props.roomCode
         }),
      };
      fetch('/api/update-room', requestOptions)
         .then((response) => {
            if (response.ok) {
               this.setState({
                  successMsg: "房间更新成功！"
               })
               this.props.updateCallback();
            } else {
               this.setState({
                  errorMsg: "房间更新失败！"
               })
            }
         });      
   }

   renderCreateButtons() {
      return (<Grid container spacing={1}>
         <Grid item xs={12} align="center">
            <Button color="primary" variant="contained" onClick={this.handleRoomButtonPressed}>创建房间</Button>
         </Grid>
         <Grid item xs={12} align="center">
            <Button color="secondary" variant="contained" to="/" component={Link}>返回房间</Button>
         </Grid>
      </Grid>
      );
   }
   renderUpdateButtons() {
      return (
         <Grid item xs={12} align="center">
            <Button color="primary" variant="contained" onClick={this.handleUpdateButtonPressed}>更新房间</Button>
         </Grid>
      );
   }



   render() {
      const title = this.props.update ? "Update Room" : "Creat a Room"

      return <Grid container spacing={1}>
         <Grid item xs={12} align="center">
            <Collapse in={this.state.errosMsg != '' || this.state.successMsg != ''}>
               {this.state.successMsg}
               {/* 这里不应该报这个，需要用一个 @material-ui/lab/lab/Alert的玩意儿，没网络下载不了。没办法。*/}
            </Collapse>
         </Grid>
         <Grid item xs={12} align="center">
            <FormControl component="fieldset">
               <FormHelperText>
                  <div align="center">游客控制状态</div>
               </FormHelperText>
               <RadioGroup 
               row 
               defaultValue= {this.props.guestCanPause.toString()} 
               onChange={this.handleGuestCanPauseChanged}
               >
                  <FormControlLabel
                     value="true"
                     control={<Radio color="primary" />}
                     label="播放/暂停"
                     labelPlacement="bottom"
                  ></FormControlLabel>
                  <FormControlLabel
                     value="false"
                     control={<Radio color="primary" />}
                     label="无控制"
                     labelPlacement="bottom"
                  ></FormControlLabel>
               </RadioGroup>
            </FormControl>
         </Grid>
         <Grid item xs={12} align="center">
            <FormControl>
               <TextField required={true} type="number" onChange={this.handleVotesChanged}
                  defaultValue={this.state.votesToSkip}
                  inputProps={{
                     mim: 1,
                     style: { textAlign: "center" }
                  }}
               ></TextField>
               <FormHelperText>
                  <div align="center">跳过歌曲所需要的投票</div>
               </FormHelperText>
            </FormControl>
         </Grid>
         {/* <Grid item xs={12} align="center">
            <Button color="primary" variant="contained" onClick={this.handleRoomButtonPressed}>创建房间</Button>
         </Grid>
         <Grid item xs={12} align="center">
            <Button color="secondary" variant="contained" to="/" component={Link}>返回房间</Button>
         </Grid> */}
         {this.props.update ? this.renderUpdateButtons() : this.renderCreateButtons()}
      </Grid>;
   }
}