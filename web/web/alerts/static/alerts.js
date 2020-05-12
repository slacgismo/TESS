import React from 'react';
import ReactDOM from 'react-dom';
import * as action from './actions';
import { connect } from 'react-redux';
import * as DT from '@rmwc/data-table';
import { TextField } from '@rmwc/textfield';
import ConnectedComponentWrapper from '../../static/js/base';

import '@rmwc/grid/styles';
import '@rmwc/textfield/styles';
import '@rmwc/data-table/styles';


class Alerts extends React.Component {
    componentDidMount() {
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
        const dataTableBody = this.props.alerts.map(item => {
            return (
                <DT.DataTableRow>
                    <DT.DataTableCell>{item.date}</DT.DataTableCell>
                    <DT.DataTableCell>{item.time}</DT.DataTableCell>
                    <DT.DataTableCell>{item.type}</DT.DataTableCell>
                    <DT.DataTableCell className="alerts-text-wrap">{item.description}</DT.DataTableCell>
                    <DT.DataTableCell>{item.status}</DT.DataTableCell>
                    <DT.DataTableCell>{item.assigned_to}</DT.DataTableCell>
                    <DT.DataTableCell>
                        <TextField outline={false} fullwidth value={item.resolution} />
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