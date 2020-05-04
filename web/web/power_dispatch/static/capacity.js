import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import ConnectedComponentWrapper from '../../static/js/base';

import * as action from './actions';

class Capacity extends React.Component {
    onClick = () => {
        this.props.dispatch(action.loginSuccessful('asdf'));
    }

    render() {
        return (
            <div>Capacity Page</div>
        );
    }
}

const ConnectedCapacity = connect(state => ({}))(Capacity);

const capacityElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedCapacity/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(capacityElement, document.getElementById('master-container'));