import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import ConnectedComponentWrapper from '../../static/base';

import * as action from './actions';

class Constraints extends React.Component {
    onClick = () => {
        this.props.dispatch(action.loginSuccessful('asdf'));
    }

    render() {
        return (
            <div>Constraints Page</div>
        );
    }
}

const ConnectedConstraints = connect(state => ({}))(Constraints)

const constraintsElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedConstraints/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(constraintsElement, document.getElementById('master-container'));