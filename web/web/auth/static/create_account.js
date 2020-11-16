import React from 'react';
import * as action from './actions';
import { Button } from '@rmwc/button';
import { TextField } from '@rmwc/textfield';
import { api } from '../../static/js/network_client';
import { menuRoutes } from '../../static/js/config/routes';
import { validateLogin } from './helpers';


import '@rmwc/button/styles';
import '@rmwc/textfield/styles';

class CreateAccount extends React.PureComponent {
    state = {
        username: "",
        password: "",
        firstName: "",
        lastName: ""
        }

    changeFirstName = (e) => {
        this.setState({firstName: e.target.value});
    }

    changeLastName = (e) => {
        this.setState({lastName: e.target.value});
    }

    changeUsername = (e) => {
        this.setState({username: e.target.value});
    }

    changePassword = (e) => {
        this.setState({password: e.target.value});
    }

    processSignUp = () => {
        const isValid = validateLogin(this.state.username, this.state.password);
        if(isValid) {
            const json = {
                json: {
                    email: this.state.username,
                    first_name: this.state.firstName,
                    last_name: this.state.lastName,
                    address_id: "11",
                    utility_id: "1"
                }
            }
            api.post("user", json, (response) => {
                const user_id = response.results.data.id;
                const login_data = {
                    json: {
                        username: this.state.username,
                        password_hash: this.state.password,
                        user_id: user_id.toString()
                    }
                }
                api.post("login", login_data, (response) => {
                    window.location.href = menuRoutes[0].path;
                }, (error) => {
                    console.warn(error);
                })
            }, (error) => {
                console.warn(error);
            })
        }
    }

    render() {
        return (
            <div className="login-page-container">
                <div className="login-form-container">
                    <div>
                        <TextField
                            onChange={(e) => this.changeUsername(e)}
                            outlined={true} 
                            label="Email" />
                    </div>
                    <br />
                    <div>
                        <TextField
                            onChange={(e) => this.changePassword(e)}
                            outlined={true}
                            type="password" 
                            label="Password" />
                    </div>
                    <br />
                    <div>
                        <TextField
                            onChange={(e) => this.changeFirstName(e)}
                            outlined={true} 
                            label="First Name" />
                    </div>
                    <br />
                    <div>
                        <TextField
                            onChange={(e) => this.changeLastName(e)}
                            outlined={true} 
                            label="Last Name" />
                    </div>
                    <br />
                    <div>
                        <Button
                            outlined
                            label="CREATE"
                            onClick={this.processSignUp} />
                    </div>
                    <br />
                    <div>
                        <Button
                            outlined
                            label="GO BACK"
                            onClick={ () => this.props.setCreateFlow(false) } />
                    </div>
                </div>
            </div>
        );
    }
}

export default CreateAccount;
