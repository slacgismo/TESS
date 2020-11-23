import React from "react";
import * as action from "./actions";
import { Button } from "@rmwc/button";
import { TextField } from "@rmwc/textfield";
import { validateLogin } from "./helpers";
import { menuRoutes } from "../../static/js/config/routes";

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

    handleSignUp = (username, firstName, lastName, password) => {
        const isValid = validateLogin(username, password);
        if (isValid) {
            this.props.authProps.dispatch(
                action.processSignUp(username, firstName, lastName, password)
            );
        }
    };

    componentDidUpdate() {
        if (this.props.authProps.isUserLoggedIn) {
            this.props.authProps.dispatch(action.resetUserLoggedIn());
            window.location.href = menuRoutes[0].path;
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
                            onClick={() =>
                                this.handleSignUp(
                                    this.state.username,
                                    this.state.firstName,
                                    this.state.lastName,
                                    this.state.password
                                )
                            }
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
