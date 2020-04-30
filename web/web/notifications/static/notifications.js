import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import ConnectedComponentWrapper from '../../static/base';

import * as action from './actions';

class Notifications extends React.Component {
    onClick = () => {
        this.props.dispatch(action.loginSuccessful('asdf'));
    }

    render() {
        return (
            <div>Notifications Page</div>
        );
    }
}

const ConnectedNotifications = connect(state => ({}))(Notifications)

const notificationsElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedNotifications/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(notificationsElement, document.getElementById('master-container'));