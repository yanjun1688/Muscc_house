import React, { Component } from 'react';
import { BrowserRouter as Router, Switch, Route, Link, Redirect } from "react-router-dom";
import RoomJoinPage from './RoomJoinPage';
import CreateRoomPage from './CreateRoomPage'
import Room from './Room';
import { Grid, Button, ButtonGroup, Typography } from '@material-ui/core'
export default class HomePage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            roomCode: null,
        };
        this.clearRoomCode = this.clearRoomCode.bind(this); 
    }

    async componentDidMount() {
        fetch('/api/user-in-room')
            .then((response) => response.json()
            )
            .then((data) => {
                this.setState({
                    roomCode: data.code
                });
            })
    }


    renderHomePage() {
        return (
            <Grid container spacing={3}>
                <Grid item xs={12} align='center'>
                    <Typography variant='h3' compact='h3'>
                        House Party
                    </Typography>
                </Grid>
                <Grid item xs={12} align='center'>
                    <ButtonGroup disableElevation variant='contained' color='primary'>
                        <Button color='primary' to='/join' component={Link}>
                            Join A Room
                        </Button>
                        <Button color='secondary' to='/create' component={Link}>
                            Creat A Room
                        </Button>
                    </ButtonGroup>
                </Grid>
            </Grid>
        );
    }
    clearRoomCode(){
        this.setState({
            roomCode:null,
        });
    }



    render() {
        return (
            // <Router>
            //     <Switch>
            //         <Route exact path='/' render={() =>{
            //             return this.state.roomCode ? (
            //             <Redirect to={`/room/${this.state.roomCode}`/}>:
            //             ):(
            //                 this.renderHomePage()
            //             );
            //             }} 
            //             />

            //             </Redirect>   
            //         </Route>
            //         <Route path='/join' component={RoomJoinPage} />
            //         <Route path='/create' component={CreateRoomPage} />
            //         <Route path='/room/:roomCode' component={Room} />
            //     </Switch>
            // </Router>
            <Router>
                <Switch>
                    {/* 首页逻辑优化 */}
                    <Route exact path="/">
                        {this.state.roomCode ? (
                            <Redirect to={`/room/${this.state.roomCode}`} />
                        ) : (
                            this.renderHomePage()
                        )}
                    </Route>

                    {/* 其他页面 */}
                    <Route path="/join" component={RoomJoinPage} />
                    <Route path="/create" component={CreateRoomPage} />
                    <Route path="/room/:roomCode" 
                    render={(props) =>{
                        return <Room {...props} leaveRoomCallback={this.clearRoomCode}></Room>
                    }} />
                </Switch>
            </Router>

        )
    }
}