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


class Storage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            day: "",
            night: "",
            yellowAlarm: "",
            redAlarm: "",
            capacityBounds: "",
            resourcesDepletion: "",
            betweenStart: "",
            betweenEnd: "",
            gridToHome: "",
            homeToGrid: ""
        };
    }

    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption('power-dispatch-storage'));
        this.props.dispatch(action.getStorageSystemLoadData());
        this.props.dispatch(action.getStorageResourcesData());
        this.setState(this.props.formData);
    }

    update = (field, event) => {
        this.setState({ [field]: event.currentTarget.value });
    }

    render() {
        const { resourcesData, systemLoadData, formData } = this.props;
        return (
            <div className="power-dispatch-container">
                <div className="power-dispatch-margin-fix">
                    <div className="power-dispatch-chart-container">
                        <div className="pd-chart-system-load">
                            {
                                // to check if data exists when calling <SystemLoadChart>
                                systemLoadData.length !== 0
                                ?
                                <SystemLoadChart
                                    id="pd-capacity-system-load-chart"
                                    ds={this.props.systemLoadData}
                                    xTitle="Hours"
                                    yTitle="kWh"
                                    chartTitle="Energy Storage"
                                    chartSubtitle="Transformer Capacity" />
                                :
                                null
                            }
                        </div>
                        <div className="pd-chart-resource">
                            {
                                // to check if data exists when calling <ResourcesChart>
                                resourcesData.datasets
                                ? <ResourcesChart
                                    id="pd-capacity-resources-chart"
                                    xTitle=""
                                    yTitle=""
                                    datasets={resourcesData.datasets}
                                    finalDataSet={resourcesData.groupedDataset}
                                    chartTitle="Resources in the System"
                                    chartSubtitle="" />
                                : null
                            }
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
                                        <TextField outlined
                                        value={this.state.day}
                                        onChange={(e) =>
                                            this.update("day", e)
                                        }
                                        onBlur={this.props.dispatch(action.saveForm(this.state))}
                                        />
                                    </div>
                                    <div className="pd-form-element-unit">MW</div>
                                </div>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Night</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined
                                        value={this.state.night}
                                        onChange={(e) =>
                                            this.update("night", e)
                                        }
                                        onBlur={this.props.dispatch(action.saveForm(this.state))}
                                        />
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
                                        <TextField outlined
                                        value={this.state.yellowAlarm}
                                        onChange={(e) =>
                                            this.update("yellowAlarm", e)
                                        }
                                        onBlur={this.props.dispatch(action.saveForm(this.state))}
                                        />
                                    </div>
                                    <div className="pd-form-element-unit">%</div>
                                </div>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Red Alarm</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined
                                        value={this.state.redAlarm}
                                        onChange={(e) =>
                                            this.update("redAlarm", e)
                                        }
                                        onBlur={this.props.dispatch(action.saveForm(this.state))}
                                        />
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
                                        <TextField outlined
                                        value={this.state.capacityBounds}
                                        onChange={(e) =>
                                            this.update("capacityBounds", e)
                                        }
                                        onBlur={this.props.dispatch(action.saveForm(this.state))}
                                        />
                                    </div>
                                    <div className="pd-form-element-unit">kW</div>
                                </div>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Resource Depletion (Battery)</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined
                                        value={this.state.resourcesDepletion}
                                        onChange={(e) =>
                                            this.update("resourcesDepletion", e)
                                        }
                                        onBlur={this.props.dispatch(action.saveForm(this.state))}
                                        />
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
                        <div className="pd-advanced-form-container">
                            <div className="pd-form-title">
                                <h3>Advanced Control</h3>
                            </div>
                            <div>
                                <h4>Override the Available Energy Quantity</h4>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Between</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined
                                        value={this.state.betweenStart}
                                        onChange={(e) =>
                                            this.update("betweenStart", e)
                                        }
                                        onBlur={this.props.dispatch(action.saveForm(this.state))}
                                        />
                                    </div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined
                                        value={this.state.betweenEnd}
                                        onChange={(e) =>
                                            this.update("betweenEnd", e)
                                        }
                                        onBlur={this.props.dispatch(action.saveForm(this.state))}
                                        />
                                    </div>
                                </div>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Grid to Home Constraint</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined
                                        value={this.state.gridToHome}
                                        onChange={(e) =>
                                            this.update("gridToHome", e)
                                        }
                                        onBlur={this.props.dispatch(action.saveForm(this.state))}
                                        />
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
                                        <TextField outlined
                                        value={this.state.homeToGrid}
                                        onChange={(e) =>
                                            this.update("homeToGrid", e)
                                        }
                                        onBlur={this.props.dispatch(action.saveForm(this.state))}
                                        />
                                    </div>
                                    <div className="pd-form-element-unit first-unit">
                                        kW
                                    </div>
                                    <div className="pd-form-element-unit second-unit">
                                        <Switch>On/Off</Switch>
                                    </div>
                                </div>
                                <hr />
                                <div className="pd-form-button-container">
                                    <Button
                                        label="SET"
                                        outlined />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

const ConnectedStorage = connect(state => ({
    systemLoadData: state.storage.systemLoadData,
    resourcesData: state.storage.resourcesData,
    formData: state.formState.formData
}))(Storage);

const storageElement = (
    <ConnectedComponentWrapper isVisible={true} pageTitle="POWER DISPATCH">
        <ConnectedStorage/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(storageElement, document.getElementById('master-container'));
