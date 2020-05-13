import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import { selectMenuOption } from '../../static/js/actions';
import ConnectedComponentWrapper from '../../static/js/base';

import * as action from './actions';

class Storage extends React.Component {
    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is 
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption('power-dispatch'));        
    }

    render() {
        return (
            <div>Storage Page</div>
        );
    }
}

const ConnectedStorage = connect(state => ({}))(Storage);

const storageElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedStorage/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(storageElement, document.getElementById('master-container'));