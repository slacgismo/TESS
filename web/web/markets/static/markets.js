import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import { selectMenuOption } from '../../static/js/actions';
import ConnectedComponentWrapper from '../../static/js/base';

import * as action from './actions';

class Markets extends React.Component {
    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is 
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption('markets'));        
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