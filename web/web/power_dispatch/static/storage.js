import React from 'react';
import ReactDOM from 'react-dom';
import * as action from './actions';
import { connect } from 'react-redux';
import { Switch } from '@rmwc/switch';
import { Button } from '@rmwc/button';
import ResourcesChart from './resources';
import SystemLoadChart from './system_load';
import { TextField } from '@rmwc/textfield';
import { selectMenuOption } from '../../static/js/actions';
import ConnectedComponentWrapper from '../../static/js/base';

import '@rmwc/switch/styles';
import '@rmwc/button/styles';
import '@rmwc/textfield/styles';


const datasets = {
    battery: [1,2,0],
    charger: [5,7,0],
    pv: [3,3,0],
    hvac: [10,15,0],
    hotWater: [12,1,0]
};
const finalDataSet = {
    "unavailable": [],
    "available": [],
    "dispatched": []
};


class Storage extends React.Component {
    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is 
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption('power-dispatch-storage'));        
    }

    render() {
        return (
            <div className="power-dispatch-container">
                <div className="power-dispatch-margin-fix">
                    <div className="power-dispatch-chart-container">
                        <div className="pd-chart-system-load">
                            <SystemLoadChart
                                id="pd-capacity-system-load-chart"
                                xTitle="Hours" 
                                yTitle="kWh" 
                                chartTitle="Energy Storage"
                                chartSubtitle="Transformer Capacity" />
                        </div>
                        <div className="pd-chart-resource">
                            <ResourcesChart
                                id="pd-capacity-resources-chart"
                                xTitle="" 
                                yTitle=""
                                datasets={datasets}
                                finalDataSet={finalDataSet}
                                hiddenDataSets={{dispatched: true}}
                                chartTitle="Resources in the System"
                                chartSubtitle="" />
                        </div>
                    </div>

                    <div className="power-dispatch-forms-container">
                        <div className="pd-form-container">
                            <div className="pd-form-title">
                                <h3>Constraint and Alert Settings</h3>
                            </div>
                            
                            <div>
                                <h4>Nominal Feeder Capacity</h4>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Day</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined />
                                    </div>
                                    <div className="pd-form-element-unit">MW</div>
                                </div>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Night</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined />
                                    </div>
                                    <div className="pd-form-element-unit">MW</div>
                                </div>
                            </div>

                            <hr />
                            
                            <div>
                                <h4>Alarms</h4>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Yellow Alarm</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined />
                                    </div>
                                    <div className="pd-form-element-unit">%</div>
                                </div>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Red Alarm</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined />
                                    </div>
                                    <div className="pd-form-element-unit">%</div>
                                </div>
                            </div>
                            
                            <hr />
                            
                            <div>
                                <h4>Alerts</h4>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Capacity Bounds</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined />
                                    </div>
                                    <div className="pd-form-element-unit">kW</div>
                                </div>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Resource Depletion (Battery)</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined />
                                    </div>
                                    <div className="pd-form-element-unit">hour(s)</div>
                                </div>
                            </div>
                            
                            <hr />
                            <div className="pd-form-button-container">
                                <Button 
                                    label="SET" 
                                    onClick={this.addNewRow}
                                    outlined />
                            </div>
                        </div>
                        
                        <div className="pd-form-container">
                            <div className="pd-form-title">
                                <h3>Advanced Control</h3>
                            </div>
                            <div>
                                <h4>Override the Available Energy Quantity</h4>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Between</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined type="time" />
                                    </div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined type="time" />
                                    </div>
                                </div>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Grid to Home Constraint</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined />
                                    </div>
                                    <div className="pd-form-element-unit first-unit">
                                        kW
                                    </div>
                                    <div className="pd-form-element-unit second-unit">
                                        <Switch>On/Off</Switch>
                                    </div>
                                </div>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Home to Grid Constraint</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined />
                                    </div>
                                    <div className="pd-form-element-unit first-unit">
                                        kW
                                    </div>
                                    <div className="pd-form-element-unit second-unit">
                                        <Switch>On/Off</Switch>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

const ConnectedStorage = connect(state => ({}))(Storage);

const storageElement = (
    <ConnectedComponentWrapper isVisible={true} pageTitle="POWER DISPATCH">
        <ConnectedStorage/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(storageElement, document.getElementById('master-container'));