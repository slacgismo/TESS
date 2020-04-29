import '@rmwc/top-app-bar/styles';

import React from 'react';
import { connect } from 'react-redux';
import { SimpleTopAppBar, TopAppBarFixedAdjust } from '@rmwc/top-app-bar';
import { toggleNavigationDrawer } from '../actions/navigation_drawer_actions';

class TopBar extends React.Component {
    toggleNavigationDrawer = () => {
        this.props.dispatch(toggleNavigationDrawer())
    }

    render() {
        return (
            <React.Fragment>
                <SimpleTopAppBar
                    title="TESS"
                    navigationIcon={true}
                    onNav={this.toggleNavigationDrawer}
                    actionItems={[
                        {
                            icon: 'exit_to_app',
                            onClick: () => console.log('logout off the application')
                        }
                    ]}
                />
                <TopAppBarFixedAdjust />
            </React.Fragment>
        );
    }
}

export default connect(state => ({}))(TopBar);