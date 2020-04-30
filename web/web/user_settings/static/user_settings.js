import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import ConnectedComponentWrapper from '../../static/base';

import * as action from './actions';

class UserSettings extends React.Component {
    onClick = () => {
        this.props.dispatch(action.loginSuccessful('asdf'));
    }

    render() {
        return (
            <div>UserSettings Page</div>
        );
    }
}

const ConnectedUserSettings = connect(state => ({}))(UserSettings);

const userSettingsElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedUserSettings/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(userSettingsElement, document.getElementById('master-container'));