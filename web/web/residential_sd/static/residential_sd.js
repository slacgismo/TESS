import React from "react";
import ReactDOM from "react-dom";
import { connect } from "react-redux";
import { selectMenuOption } from "../../static/js/actions";
import ConnectedComponentWrapper from '../../static/js/base';
import EnergyDemandChart from './energy_demand';
import EnergySupplyChart from './energy_supply';

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
            <div className="power-dispatch-container">
                <div className="power-dispatch-margin-fix">
                    <div className="power-dispatch-chart-container">
                        <div className="pd-chart-energy-demand">
                            <EnergySupplyChart
                                id="pd-capacity-system-load-chart"
                                xTitle="Date"
                                yTitle="kWh"
                                chartTitle="Daily Energy Supply - per Resource"
                                chartSubtitle="Transformer Capacity" />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

const ConnectedResidentialSD = connect(state => ({
    systemLoadData: state.storage.systemLoadData,
    resourcesData: state.storage.resourcesData,
    formData: state.formState.formData
}))(ResidentialSD);

const residentialSDElement = (
    <ConnectedComponentWrapper isVisible={true} pageTitle="RESIDENTIAL S&D">
        <ConnectedResidentialSD/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(residentialSDElement, document.getElementById('master-container'));
