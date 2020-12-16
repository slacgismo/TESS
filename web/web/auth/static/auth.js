import React from "react";
import ReactDOM from "react-dom";
import * as action from "./actions";
import { connect } from "react-redux";
import { Button } from "@rmwc/button";
import { TextField } from "@rmwc/textfield";
import CreateAccount from "./create_account";
import { menuRoutes } from "../../static/js/config/routes";
import ConnectedComponentWrapper from "../../static/js/base";
import { validateLoginData } from "../../static/js/helpers";

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
        this.props.dispatch(
            action.processLogin(this.state.username, this.state.password)
        );
    };

    componentDidUpdate() {
        if (this.props.isUserLoggedIn) {
            this.props.dispatch(action.resetUserLoggedIn());
            window.location.href = menuRoutes[0].path;
        }
    }

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
    isUserLoggedIn: state.auth.userLoggedIn,
    userData: state.auth.userData,
}))(Auth);

const authElement = (
    <ConnectedComponentWrapper isVisible={false}>
        <ConnectedAuth />
    </ConnectedComponentWrapper>
);
ReactDOM.render(authElement, document.getElementById("master-container"));
