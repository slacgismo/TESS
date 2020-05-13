import React from 'react';
import ReactDOM from 'react-dom';
import * as action from './actions';
import { connect } from 'react-redux';
import * as DT from '@rmwc/data-table';
import { TextField } from '@rmwc/textfield';
import { selectMenuOption } from '../../static/js/actions';
import ConnectedComponentWrapper from '../../static/js/base';

import '@rmwc/textfield/styles';
import '@rmwc/data-table/styles';

class Alerts extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            inputValueReferences: {}
        };
    }
    
    handleChange = (event, id) => {        
        let refs = this.state.inputValueReferences;
        refs[id] = event.target.value;
        this.setState({inputValueReferences: refs});
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
                    <DT.DataTableHeadCell>Date</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell>Time</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell>Type</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell>Description</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell>Status</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell>Assigned To</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell>Resolution</DT.DataTableHeadCell>
                </DT.DataTableRow>
            </DT.DataTableHead>
        );
    }

    getBody = () => {
        const dataTableBody = this.props.alerts.map((item, index) => {
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
                    <DT.DataTableCell>{item.status}</DT.DataTableCell>
                    <DT.DataTableCell>{item.assigned_to}</DT.DataTableCell>
                    <DT.DataTableCell>
                        <TextField
                            onChange={(e) => this.handleChange(e, index)}
                            outlined={false} 
                            fullwidth={true} 
                            align="start" 
                            value={resolutionValue} />
                    </DT.DataTableCell>
                </DT.DataTableRow>
            )
        });

        return (<DT.DataTableBody>{dataTableBody}</DT.DataTableBody>);
    }

    render() {
        return (
            <div>
                <div className="alert-search-bar">
                    <TextField fullwidth icon="search" trailingIcon="close" label="Search" />
                </div>
                <DT.DataTable className="alerts-data-table">
                    <DT.DataTableContent>
                        {this.getHeader()}
                        {this.getBody()}
                    </DT.DataTableContent>
                </DT.DataTable>
            </div>
        );
    }
}

const ConnectedAlerts = connect(state => ({
    alerts: state.alerts.alertEntries
}))(Alerts);

const alertsElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedAlerts/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(alertsElement, document.getElementById('master-container'));