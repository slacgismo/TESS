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

const tempData = [
    {
        "date": "2020-01-01",
        "time": "19:20",
        "type": "Capacity Bounds",
        "description": "Lorem Ipsum dolor sit amet....",
        "status": "Pending",
        "assigned_to": "Operator 1",
        "resolution": "A random resolution input"
    },
    {
        "date": "2020-01-02",
        "time": "19:30",
        "type": "Resource Depletion",
        "description": "Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....",
        "status": "Resolved",
        "assigned_to": "Automated System",
        "resolution": ""
    },
    {
        "date": "2020-01-21",
        "time": "08:20",
        "type": "Price Alerts",
        "description": "Lorem Ipsum dolor sit amet....",
        "status": "Open",
        "assigned_to": "SLAC Gismo",
        "resolution": ""
    },
    {
        "date": "2020-01-22",
        "time": "09:20",
        "type": "Capacity Bounds",
        "description": "Lorem Ipsum dolor sit amet....",
        "status": "Resolved",
        "assigned_to": "SLAC Gismo",
        "resolution": "I resolved this somehow"
    },
    {
        "date": "2020-01-23",
        "time": "18:20",
        "type": "Resource Depletion",
        "description": "Lorem Ipsum dolor sit amet...Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet.....",
        "status": "Resolved",
        "assigned_to": "Automated System",
        "resolution": "system recovered"
    },
    {
        "date": "2020-01-24",
        "time": "19:20",
        "type": "Price Alerts",
        "description": "Lorem Ipsum dolor sit amet....",
        "status": "Open",
        "assigned_to": "Operator 2",
        "resolution": "Resolved"
    },
    {
        "date": "2020-01-25",
        "time": "20:20",
        "type": "Capacity Bounds",
        "description": "Lorem Ipsum dolor sit amet..Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet......",
        "status": "Pending",
        "assigned_to": "Operator 1",
        "resolution": "Resolved"
    }
]

class Alerts extends React.Component {
    onClick = () => {
        this.props.dispatch(action.loginSuccessful('asdf'));
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
        )
    }

    getBody = () => {
        const dataTableBody = tempData.map(item => {
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
        })

        return (<DT.DataTableBody>{dataTableBody}</DT.DataTableBody>)
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

const ConnectedAlerts = connect(state => ({}))(Alerts);

const alertsElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedAlerts/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(alertsElement, document.getElementById('master-container'));