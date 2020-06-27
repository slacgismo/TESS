import React from 'react';
import * as action from './actions';
import { Button } from '@rmwc/button';
import { TextField } from '@rmwc/textfield';

import '@rmwc/button/styles';
import '@rmwc/textfield/styles';

class CreateAccount extends React.PureComponent {
    state = {
        username: "",
        password: "",
        firstName: "",
        lastName: ""
    }

    render() {
        return (
            <div className="login-page-container">
                <div className="login-form-container">
                    <div>
                        <TextField
                            onChange={(e) => this.handleUsernameChange(e)}
                            outlined={true} 
                            label="Email" />
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
                        <TextField
                            onChange={(e) => this.handleUsernameChange(e)}
                            outlined={true} 
                            label="First Name" />
                    </div>
                    <br />
                    <div>
                        <TextField
                            onChange={(e) => this.handleUsernameChange(e)}
                            outlined={true} 
                            label="Last Name" />
                    </div>
                    <br />
                    <div>
                        <Button
                            outlined
                            label="CREATE"
                            onClick={this.handleLogin} />
                    </div>
                    <br />
                    <div>
                        <Button
                            outlined
                            label="GO BACK"
                            onClick={() => this.props.setCreateFlow(false)} />
                    </div>
                </div>
            </div>
        );
    }
}

export default CreateAccount;
