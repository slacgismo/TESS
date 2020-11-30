import '@rmwc/top-app-bar/styles';

import React from 'react';
import { connect } from 'react-redux';
import { SimpleTopAppBar, TopAppBarFixedAdjust } from '@rmwc/top-app-bar';
import { toggleNavigationDrawer, logout } from '../actions';


class TopBar extends React.Component {
    toggleNavigationDrawer = () => {
        this.props.dispatch(toggleNavigationDrawer());
    }

    logoutOfTess = () => {
        console.log("logging out of the application, will need to clear the token cache");
        this.props.dispatch(logout());
    }

    render() {
        if(!this.props.isVisible) {
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
                            icon: 'exit_to_app',
                            onClick: this.logoutOfTess
                        }
                    ]}
                />
                <TopAppBarFixedAdjust />
            </React.Fragment>
        );
    }
}

export default connect(state => ({}))(TopBar);