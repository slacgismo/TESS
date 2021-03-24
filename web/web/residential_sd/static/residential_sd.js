import React from "react";
import ReactDOM from "react-dom";
import { connect } from "react-redux";
import { selectMenuOption } from "../../static/js/actions";
import ConnectedComponentWrapper from '../../static/js/base';

import * as action from './actions';

class ResidentialSD extends React.Component {
    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption('residential-sd'));
    }
    render() {
        return (
            <h1> This is the Residential SD page </h1>
        );
    }
}

const ConnectedResidentialSD = connect(state => ({}))(ResidentialSD);

const residentialSDElement = (
    <ConnectedComponentWrapper isVisible={true} pageTitle="RESIDENTIAL S&D">
        <ConnectedResidentialSD/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(residentialSDElement, document.getElementById('master-container'));
