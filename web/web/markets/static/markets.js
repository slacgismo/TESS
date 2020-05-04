import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import ConnectedComponentWrapper from '../../static/js/base';

import * as action from './actions';

class Markets extends React.Component {
    onClick = () => {
        this.props.dispatch(action.loginSuccessful('asdf'));
    }

    render() {
        return (
            <div>Markets Page</div>
        );
    }
}

const ConnectedMarkets = connect(state => ({}))(Markets);

const marketsElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedMarkets/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(marketsElement, document.getElementById('master-container'));