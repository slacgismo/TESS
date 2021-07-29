import React from 'react';
import ReactDOM from 'react-dom';
import * as action from './actions';
import { connect } from 'react-redux';
import * as DT from '@rmwc/data-table';
import { Select } from '@rmwc/select';
import { TextField } from '@rmwc/textfield';
import { selectMenuOption } from '../../static/js/actions';
import ConnectedComponentWrapper from '../../static/js/base';

import '@rmwc/select/styles';
import '@rmwc/textfield/styles';
import '@rmwc/data-table/styles';

class Alerts extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            inputValueReferences: {},
            searchEmailObj: null
        };
    }

    handleChange = (e, id) => {
        let refs = this.state.inputValueReferences;
        refs[id] = e.target.value;
        this.setState({inputValueReferences: refs});
    }

    handleResolutionChange = (e, alert) => {
        this.props.dispatch(action.updateAlerts({
            "alert_id" : alert.alert_id,
            "alert_type_id" : alert.alert_type_id,
            "assigned_to" : alert.assigned_to,
            "description" : alert.description,
            "status" : alert.status,
            "resolution" : e.target.value
        }))
    }

    handleStatusChange = (e, alert) => {
        this.props.dispatch(action.updateAlerts({
            "alert_id" : alert.alert_id,
            "alert_type_id" : alert.alert_type_id,
            "assigned_to" : alert.assigned_to,
            "description" : alert.description,
            "status" : e.currentTarget.value,
            "resolution" : alert.resolution
        }))
    }

    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption('alerts'));
        this.props.dispatch(action.getAlerts());
    }

    getHeader = () => {
        return (
            <DT.DataTableHead>
                <DT.DataTableRow>
                    <DT.DataTableHeadCell className="alerts-header">Date</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell className="alerts-header">Time</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell className="alerts-header">Type</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell className="alerts-header">Description</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell className="alerts-header">Assigned To</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell className="alerts-header">Resolution</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell className="alerts-header">Status</DT.DataTableHeadCell>
                </DT.DataTableRow>
            </DT.DataTableHead>
        );
    }

    getBody = (emailObj) => {
        const dataTableBody = emailObj.map((item, index) => {
            // if there's a value and the user removes it, we want to persist
            // the removal, so we check if it's an empty string
            const resolutionValue = this.state.inputValueReferences[index] === ""
                ? this.state.inputValueReferences[index]
                : this.state.inputValueReferences[index] || item.resolution;
            return (
                <DT.DataTableRow>
                    <DT.DataTableCell>{item.date}</DT.DataTableCell>
                    <DT.DataTableCell>{item.time}</DT.DataTableCell>
                    <DT.DataTableCell>{item.alert_type}</DT.DataTableCell>
                    <DT.DataTableCell className="alerts-text-wrap">{item.description}</DT.DataTableCell>
                    <DT.DataTableCell>{item.assigned_to}</DT.DataTableCell>
                    <DT.DataTableCell>
                        <TextField
                            onChange={(e) => this.handleChange(e, index)}
                            onBlur={(e) => this.handleResolutionChange(e, item)}
                            outlined={false}
                            fullwidth={true}
                            align="start"
                            value={resolutionValue} />
                    </DT.DataTableCell>
                    <Select
                        defaultValue={item.status}
                        enhanced
                        options={["open", "pending", "resolved"]}
                        onChange={(e) => this.handleStatusChange(e, item)}
                    />
                </DT.DataTableRow>

            )
        });

        return (<DT.DataTableBody>{dataTableBody}</DT.DataTableBody>);
    }

    handleEmailSearch = async (e) => {
      const searchValue = e.target.value
      let newEmailObj = await alert.alertEntries.map((alert) => {
         if (alert.assigned_to.slice(0, searchValue.length) === searchValue){
             return alert
         }
      })
       let filteredEmailObj = await newEmailObj.filter(x => x !== undefined)
       this.setState({["searchEmailObj"]: filteredEmailObj})
    }

    render() {
        return (
            <div>
                <div className="alerts-search-bar">
                    <TextField
                        icon="search"
                        trailingIcon="close"
                        label="Search"
                        onChange={ e => this.handleEmailSearch(e) }
                    />
                </div>
                <div className="alerts-data-table">
                    <DT.DataTableContent>
                        { this.getHeader() }
                        {
                          (this.state.searchEmailObj !== null)
                          ?
                          this.getBody(this.state.searchEmailObj)
                          :
                          this.getBody(alert.alertEntries)
                        }
                    </DT.DataTableContent>
                </div>
            </div>
        );
    }
}

const ConnectedAlerts = connect(state => ({
    alerts: state.alerts.alertEntries
}))(Alerts);

const alertsElement = (
    <ConnectedComponentWrapper isVisible={true} pageTitle="ALERTS">
        <ConnectedAlerts/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(alertsElement, document.getElementById('master-container'));
