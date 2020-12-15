import "@rmwc/top-app-bar/styles";

import React from "react";
import { connect } from "react-redux";
import { SimpleTopAppBar, TopAppBarFixedAdjust } from "@rmwc/top-app-bar";
import { toggleNavigationDrawer, completeLogout, resetUserLoggedOut } from "../actions";
import { createErrorMessage } from "../helpers";
import { api } from "../network_client";

class TopBar extends React.Component {
    toggleNavigationDrawer = () => {
        this.props.dispatch(toggleNavigationDrawer());
    };

    logout = () => {
        try {
            api.delete(
                "logout",
                { json: { logout: true } },
                () => {
                    this.props.dispatch(completeLogout());
                },
                () => {
                    createErrorMessage("Error", "Unable to logout");
                }
            );
        } catch (error) {
            createErrorMessage("Server error", "Something went wrong");
        }
    };

    componentDidUpdate() {
        if (this.props.userLoggedOut) {
            window.location.href = "/";
        }
    }

    render() {
        if (!this.props.isVisible) {
            return null;
        }

        return (
            <React.Fragment>
                <SimpleTopAppBar
                    className="top-app-bar"
                    title="TESS"
                    navigationIcon={true}
                    onNav={this.toggleNavigationDrawer}
                    actionItems={[
                        {
                            icon: "exit_to_app",
                            onClick: this.logout,
                        },
                    ]}
                />
                <TopAppBarFixedAdjust />
            </React.Fragment>
        );
    }
}

export default connect((state) => ({
    userLoggedOut: state.drawerNavigationMenu.userLoggedOut,
}))(TopBar);
