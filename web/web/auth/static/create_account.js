import React from "react";
import * as action from "./actions";
import { Button } from "@rmwc/button";
import { TextField } from "@rmwc/textfield";
import { validateLogin } from "./helpers";

import "@rmwc/button/styles";
import "@rmwc/textfield/styles";

class CreateAccount extends React.PureComponent {
    state = {
        username: "",
        password: "",
        firstName: "",
        lastName: "",
    };

    changeFirstName = (e) => {
        this.setState({ firstName: e.target.value });
    };

    changeLastName = (e) => {
        this.setState({ lastName: e.target.value });
    };

    changeUsername = (e) => {
        this.setState({ username: e.target.value });
    };

    changePassword = (e) => {
        this.setState({ password: e.target.value });
    };

    processSignUp = () => {
        const isValid = validateLogin(this.state.username, this.state.password);
        if (isValid) {
            this.props.authProps.dispatch(
                action.processSignUp(
                    this.state.username,
                    this.state.firstName,
                    this.state.lastName,
                    this.state.password
                )
            );
        }
    };

    render() {
        return (
            <div className="login-page-container">
                <div className="login-form-container">
                    <div>
                        <TextField
                            onChange={(e) => this.changeUsername(e)}
                            outlined={true}
                            label="Email"
                        />
                    </div>
                    <br />
                    <div>
                        <TextField
                            onChange={(e) => this.changePassword(e)}
                            outlined={true}
                            type="password"
                            label="Password"
                        />
                    </div>
                    <br />
                    <div>
                        <TextField
                            onChange={(e) => this.changeFirstName(e)}
                            outlined={true}
                            label="First Name"
                        />
                    </div>
                    <br />
                    <div>
                        <TextField
                            onChange={(e) => this.changeLastName(e)}
                            outlined={true}
                            label="Last Name"
                        />
                    </div>
                    <br />
                    <div>
                        <Button
                            outlined
                            label="CREATE"
                            onClick={this.processSignUp}
                        />
                    </div>
                    <br />
                    <div>
                        <Button
                            outlined
                            label="GO BACK"
                            onClick={() => this.props.setCreateFlow(false)}
                        />
                    </div>
                </div>
            </div>
        );
    }
}

export default CreateAccount;
