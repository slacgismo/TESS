import React from 'react';
import ReactDOM from 'react-dom';
import * as action from './actions';
import { connect } from 'react-redux';
import * as DT from '@rmwc/data-table';
import { Grid, GridCell } from '@rmwc/grid';
import { TextField } from '@rmwc/textfield';
import ConnectedComponentWrapper from '../../static/js/base';

import '@rmwc/grid/styles';
import '@rmwc/textfield/styles';
import '@rmwc/data-table/styles';

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
        return (
            <DT.DataTableBody>
                <DT.DataTableRow>
                    <DT.DataTableCell>Cookies</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>25</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>$2.90</DT.DataTableCell>
                    <DT.DataTableCell>Cookies</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>25</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>$2.90</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>$2.90</DT.DataTableCell>
                </DT.DataTableRow>
                <DT.DataTableRow selected>
                    <DT.DataTableCell>zxcvzxcv</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>2225</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>$22.90</DT.DataTableCell>
                    <DT.DataTableCell>zxcvzxcv</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>25</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>$211.90</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>$112.90</DT.DataTableCell>
                </DT.DataTableRow>
                <DT.DataTableRow>
                    <DT.DataTableCell>asdfasdf</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>24565</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>$2.90</DT.DataTableCell>
                    <DT.DataTableCell>asdfadsf</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>245</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>$24.90</DT.DataTableCell>
                    <DT.DataTableCell alignEnd>$2444.90</DT.DataTableCell>
                </DT.DataTableRow>
            </DT.DataTableBody>
        )
    }

    render() {
        return (
            <div>
                <div className="alert-search-bar">
                    <TextField icon="search" trailingIcon="close" label="Search" />
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