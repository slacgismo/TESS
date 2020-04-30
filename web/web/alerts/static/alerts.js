import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import ConnectedComponentWrapper from '../../static/base';

import * as action from './actions';

class Alerts extends React.Component {
    onClick = () => {
        this.props.dispatch(action.loginSuccessful('asdf'));
    }

    render() {
        return (
            <div>Alerts Page</div>
        );
    }
}

const ConnectedAlerts = connect(state => ({}))(Alerts)

const alertsElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedAlerts/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(alertsElement, document.getElementById('master-container'));