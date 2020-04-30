import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import ConnectedComponentWrapper from '../../static/base';

import * as action from './actions';

class Storage extends React.Component {
    onClick = () => {
        this.props.dispatch(action.loginSuccessful('asdf'));
    }

    render() {
        return (
            <div>Storage Page</div>
        );
    }
}

const ConnectedStorage = connect(state => ({}))(Storage)

const storageElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedStorage/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(storageElement, document.getElementById('master-container'));