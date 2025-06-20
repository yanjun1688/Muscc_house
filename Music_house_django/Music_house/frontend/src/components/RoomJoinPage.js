import React, { Component } from 'react';
import { TextField, Button, Grid, Typography } from "@material-ui/core";
import { Link } from "react-router-dom";
export default class RoomJoinPage extends Component {
   constructor(props) {
      super(props);
      this.state = {
         roomCode: "",
         error: "",
      }
      this.handleTextFieldChange = this.handleTextFieldChange.bind(this);
      this.roomButtonPressed = this.roomButtonPressed.bind(this);
   }
   render() {
      return (
         <Grid container spacing={1} alignItems='center'>
            <Grid item xs={12} align="center">
               <Typography variant='h4' component='h4'>
                  加入一个房间
               </Typography>
            </Grid>
            <Grid item xs={12} align="center">
               <TextField
                  error={this.state.error}
                  label="Code"
                  placeholder='输入房间号'
                  value={this.state.roomCode}
                  helperText={this.state.error}
                  variant='outlined'
                  onChange={this.handleTextFieldChange}
               >
               </TextField>
            </Grid>
            <Grid item xs={12} align="center">
               <Button variant='contained' color='primary' onClick={this.roomButtonPressed}>确定</Button>
            </Grid>
            <Grid item xs={12} align="center">
               <Button variant='contained' color='secondary' to='/' component={Link}>返回</Button>
            </Grid>
         </Grid>
      )
   }
   handleTextFieldChange(e) {
      this.setState({
         roomCode: e.target.value,
      });
   }
   roomButtonPressed() {
      console.log(this.state.roomCode);
      const requestOptions = {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({
            code: this.state.roomCode
         })
      };
      fetch('api/join-room', requestOptions).then((response) => {
         if (response.ok) {
            this.props.history.push(`/room/${this.state.roomCode}`)
         } else {
            this.setState({error:"Room not found"})
         }
      }).catch((error) => {
         console.log("请求失败:", error);
      })
   }
}