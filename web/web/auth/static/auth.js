import React from 'react';
import ReactDOM from 'react-dom';
import * as action from './actions';
import { connect } from 'react-redux';
import { Button } from '@rmwc/button';
import { TextField } from '@rmwc/textfield';
import CreateAccount from './create_account';
import { menuRoutes } from '../../static/js/config/routes';
import ConnectedComponentWrapper from '../../static/js/base';
import { queue } from '../../static/js/components/app_notification_queue';

import '@rmwc/textfield/styles';
import '@material/button/dist/mdc.button.css';

class Auth extends React.Component {
    state = {
        username: "",
        password: "",
        userIsCreatingAccount: false
    }

    handleUsernameChange = (e) => {
        this.setState({username: e.target.value});
    }

    handlePasswordChange = (e) => {
        this.setState({password: e.target.value});
    }

    handleLogin = () => {
        let valid = true;
        if(!~this.state.username.indexOf("@")) {
            valid = false;
            // validate the email contains at least an @ symbol
            queue.notify({
                title: <b>Username</b>,
                body: 'Must be a valid email in the format: "someone@somewhere.com"',
                dismissesOnAction: true,
                timeout: -1,
                actions: [{title: 'Dismiss'}]
            });
        }

        if(this.state.password.length < 8) {
            valid = false;
            // validate the password is at least eight chars long
            // validate the username is not empty
            queue.notify({
                title: <b>Password</b>,
                body: 'Must be at least 8 characters long',
                dismissesOnAction: true,
                timeout: -1,
                actions: [{title: 'Dismiss'}]
            })
        }

        if(valid) {
            window.location.href = menuRoutes[0].path;
        }
    }

    setUserCreateFlow = (isInCreateFlow) => {
        this.setState({userIsCreatingAccount: isInCreateFlow})
    }

    render() {
        if(this.state.userIsCreatingAccount) {
            return (
                <div className="create-account-page-container">
                    <div className="create-account-form-container">
                        <CreateAccount setCreateFlow={this.setUserCreateFlow} />
                    </div>
                </div>
            );
        }

        return (
            <div className="login-page-container">
                <div className="login-form-container">
                    <div>
                        <TextField
                            onChange={(e) => this.handleUsernameChange(e)}
                            outlined={true} 
                            label="Username" />
                    </div>
                    <br />
                    <div>
                        <TextField
                            onChange={this.handlePasswordChange}
                            outlined={true}
                            type="password" 
                            label="Password" />
                    </div>
                    <br />
                    <div>
                        <Button
                            unelevated
                            label="LOGIN"
                            onClick={this.handleLogin} />
                    </div>
                    <hr />
                    <div>
                        <Button
                            unelevated
                            label="SIGN UP"
                            onClick={() => this.setUserCreateFlow(true)} />
                    </div>
                </div>
            </div>
        );
    }
}

const ConnectedAuth = connect(state => ({
    token: state.auth.token
  }))(Auth)

const authElement = (
    <ConnectedComponentWrapper isVisible={false}>
        <ConnectedAuth/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(authElement, document.getElementById('master-container'));