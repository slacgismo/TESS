import React from "react";
import ReactDOM from "react-dom";
import * as action from "./actions";
import { connect } from "react-redux";
import { Button } from "@rmwc/button";
import { TextField } from "@rmwc/textfield";
import CreateAccount from "./create_account";
import ConnectedComponentWrapper from "../../static/js/base";
import { validateLogin } from "./helpers";

import "@rmwc/button/styles";
import "@rmwc/textfield/styles";

class Auth extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            username: "",
            password: "",
            userIsCreatingAccount: false,
        };
    }

    handleUsernameChange = (e) => {
        this.setState({ username: e.target.value });
    };

    handlePasswordChange = (e) => {
        this.setState({ password: e.target.value });
    };

    setUserCreateFlow = (isInCreateFlow) => {
        this.setState({ userIsCreatingAccount: isInCreateFlow });
    };

    handleLogin = () => {
        const isValid = validateLogin(this.state.username, this.state.password);
        if (isValid) {
            this.props.dispatch(
                action.processLogin(this.state.username, this.state.password)
            );
        }
    };

    render() {
        if (this.state.userIsCreatingAccount) {
            return (
                <div className="create-account-page-container">
                    <div className="create-account-form-container">
                        <CreateAccount
                            authProps={this.props}
                            setCreateFlow={(isInCreateFlow) =>
                                this.setUserCreateFlow(isInCreateFlow)
                            }
                        />
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
                            label="Username"
                        />
                    </div>
                    <br />
                    <div>
                        <TextField
                            onChange={this.handlePasswordChange}
                            outlined={true}
                            type="password"
                            label="Password"
                        />
                    </div>
                    <br />
                    <div>
                        <Button
                            outlined
                            label="LOGIN"
                            onClick={this.handleLogin}
                        />
                    </div>
                    <br />
                    <div>
                        <Button
                            outlined
                            label="SIGN UP"
                            onClick={() => this.setUserCreateFlow(true)}
                        />
                    </div>
                </div>
            </div>
        );
    }
}

const ConnectedAuth = connect((state) => ({
    token: state.auth.token,
}))(Auth);

const authElement = (
    <ConnectedComponentWrapper isVisible={false}>
        <ConnectedAuth />
    </ConnectedComponentWrapper>
);
ReactDOM.render(authElement, document.getElementById("master-container"));
