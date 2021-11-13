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


class Capacity extends React.Component {
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
            gridToHomeSwitch: false,
            homeToGrid: "",
            homeToGridSwitch: false
        };
    }

    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption('power-dispatch-capacity'));
        this.props.dispatch(action.getCapacitySystemLoadData());
        this.props.dispatch(action.getCapacityResourcesData());
        this.props.dispatch(action.getTransformerData());
        this.props.dispatch(action.getAlertSettings());
        this.setState(this.props.formData);
        if (typeof this.props.transformerData!=="undefined") {
            this.setState({day: this.props.transformerData["import_capacity"]})
        }
        if (typeof this.props.alertSettings!=="undefined") {
            this.setState({
                yellowAlarm: this.props.alertSettings["yellow_alarm_percentage"],
                redAlarm: this.props.alertSettings["red_alarm_percentage"],
                capacityBounds: this.props.alertSettings["capacity_bound"],
                resourcesDepletion: this.props.alertSettings["resource_depletion"]
            })
        }
    }

    update = (field, event) => {
        this.setState({ [field]: event.currentTarget.value });
    }

    updateSwitch = (field, event) => {
        this.setState({ [field]: !!event.currentTarget.checked});
        this.props.dispatch(action.saveForm(this.state));
    }

    updateFormData = () => {
        let transformerData = {
            "import_capacity": this.state.day,
            "end_time": null,
            "export_capacity": null,
            "q": null,
            "start_time": null,
            "transformer_id": 1,
            "unresp_load": null
        }
        this.props.dispatch(action.postTransformerIntervalData(transformerData))

        let alertSettings = {
            "capacity_bound": this.state.capacityBounds,
            "red_alarm_percentage": this.state.redAlarm,
            "resource_depletion": this.state.resourcesDepletion,
            "utility_id": 1,
            "yellow_alarm_percentage": this.state.yellowAlarm
        }
        this.props.dispatch(action.postAlertSettingsData(alertSettings))

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
                                    yTitle="kW"
                                    chartTitle="System Load"
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
                                    <div className="pd-form-element-unit">kW</div>
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
                                    <div className="pd-form-element-unit">kW</div>
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
                                    outlined
                                    onClick={this.updateFormData} />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}
const ConnectedCapacity = connect(state => ({
    systemLoadData: state.capacity.systemLoadData,
    resourcesData: state.capacity.resourcesData,
    formData: state.formState.formData,
    transformerData: state.transformerDataState.transformerData,
    alertSettings: state.alertSettingsState.alertSettings
}))(Capacity);

const capacityElement = (
    <ConnectedComponentWrapper isVisible={true} pageTitle="CAPACITY">
        <ConnectedCapacity/>
    </ConnectedComponentWrapper>
);

ReactDOM.render(capacityElement, document.getElementById('master-container'));
