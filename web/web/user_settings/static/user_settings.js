import React from "react";
import ReactDOM from "react-dom";
import * as action from "./actions";
import { connect } from "react-redux";
import { ListDivider } from "@rmwc/list";
import { TextField } from "@rmwc/textfield";
import { Typography } from "@rmwc/typography";
import { selectMenuOption } from "../../static/js/actions";
import ConnectedComponentWrapper from "../../static/js/base";
import {
    Card,
    CardPrimaryAction,
    CardActions,
    CardActionButton,
} from "@rmwc/card";

import "@rmwc/card/styles";
import "@rmwc/list/styles";
import "@rmwc/textfield/styles";
import "@rmwc/typography/styles";
import { validateUserSettingsInfo } from "./helpers";

class UserSettings extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            username: this.props.userData.username,
            password: "",
            firstName: this.props.userData.first_name,
            lastName: this.props.userData.last_name,
        };
    }

    handleStateChange = (field, e) => {
        this.setState({ [field]: e.target.value });
    };

    handleSaveSettings = () => {
        const isValid = validateUserSettingsInfo(
            this.state.username,
            this.state.password
        );
        if (isValid) {
            this.props.dispatch(
                action.updateUserSettings(
                    this.props.userData.user_id,
                    this.state.username,
                    this.state.password,
                    this.state.firstName,
                    this.state.lastName
                )
            );
        }
    };

    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption("user-settings"));
    }

    render() {
        return (
            <Card
                className="user-settings-container"
                outlined
                style={{ width: "700px", margin: "20px auto" }}
            >
                <Typography
                    use="subtitle1"
                    tag="div"
                    style={{ padding: "0.5rem 1rem" }}
                >
                    User Settings
                </Typography>

                <ListDivider />

                <CardPrimaryAction>
                    <div style={{ padding: "1rem" }}>
                        <Typography use="headline5" tag="div">
                            Username
                        </Typography>
                        <Typography use="body1" tag="p">
                            Sorry but you can't change your username right now
                        </Typography>
                        <TextField
                            onChange={(e) =>
                                this.handleStateChange("username", e)
                            }
                            value={this.state.username}
                        />
                    </div>
                </CardPrimaryAction>

                <ListDivider />

                <CardPrimaryAction>
                    <div style={{ padding: "1rem" }}>
                        <Typography use="headline5" tag="div">
                            Password
                        </Typography>
                        <Typography use="body1" tag="p">
                            Your password must be at least 8 characters long
                        </Typography>
                        <TextField
                            onChange={(e) =>
                                this.handleStateChange("password", e)
                            }
                            type="password"
                            placeholder="********"
                        />
                    </div>
                </CardPrimaryAction>

                <ListDivider />

                <CardPrimaryAction>
                    <div style={{ padding: "1rem" }}>
                        <Typography use="headline5" tag="div">
                            First Name
                        </Typography>
                        <Typography use="body1" tag="p"></Typography>
                        <TextField
                            onChange={(e) =>
                                this.handleStateChange("firstName", e)
                            }
                            value={this.state.firstName}
                        />
                    </div>
                </CardPrimaryAction>

                <ListDivider />

                <CardPrimaryAction>
                    <div style={{ padding: "1rem" }}>
                        <Typography use="headline5" tag="div">
                            Last Name
                        </Typography>
                        <Typography use="body1" tag="p"></Typography>
                        <TextField
                            onChange={(e) =>
                                this.handleStateChange("lastName", e)
                            }
                            value={this.state.lastName}
                        />
                    </div>
                </CardPrimaryAction>

                <ListDivider />

                <CardActions fullBleed>
                    <CardActionButton
                        onClick={this.handleSaveSettings}
                        label="Save Changes"
                    />
                </CardActions>
            </Card>
        );
    }
}

const ConnectedUserSettings = connect((state) => ({
    userData: state.userSettings.userData,
}))(UserSettings);

const userSettingsElement = (
    <ConnectedComponentWrapper isVisible={true} pageTitle="USER SETTINGS">
        <ConnectedUserSettings />
    </ConnectedComponentWrapper>
);
ReactDOM.render(
    userSettingsElement,
    document.getElementById("master-container")
);
