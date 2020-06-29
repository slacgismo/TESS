import React from 'react';
import ReactDOM from 'react-dom';
import * as action from './actions';
import { v4 as uuidv4 } from 'uuid';
import { connect } from 'react-redux';
import { Button } from '@rmwc/button';
import * as DT from '@rmwc/data-table';
import { Checkbox } from '@rmwc/checkbox';
import { TextField } from '@rmwc/textfield';
import { selectMenuOption } from '../../static/js/actions';
import ConnectedComponentWrapper from '../../static/js/base';

import '@rmwc/button/styles';
import '@rmwc/checkbox/styles';
import '@rmwc/textfield/styles';
import '@rmwc/data-table/styles';

const defaultHeaders = [
    { "is_active": false, "notification_type": "YELLOW_ALARM_LOAD", "label": "Yellow Alarm (Load)" },
    { "is_active": false, "notification_type": "TELECOMM_ALERTS", "label": "Telecomm Alerts" },
    { "is_active": false, "notification_type": "RED_ALARM_LOAD", "label": "Red Alarm (Load)" },
    { "is_active": false, "notification_type": "RED_ALARM_PRICE", "label": "Red Alarm (Price)" },
    { "is_active": false, "notification_type": "YELLOW_ALARM_PRICE", "label": "Yellow Alarm (Price)" },
    { "is_active": false, "notification_type": "CAPACITY_BOUNDS", "label": "Capacity Bounds" },
    { "is_active": false, "notification_type": "RESOURCE_DEPLETION", "label": "Resource Depletion" },
    { "is_active": false, "notification_type": "PRICE_ALERTS", "label": "Price Alerts" }
]

class Notifications extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            checkboxReferences: {},
            inputValueReferences: {},
            selectedRowIdsToDelete: []
        };
    }

    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is 
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption('notifications'));
        this.props.dispatch(action.getNotifications());
    }

    handleEmailChange = (e, id) => {
        let refs = this.state.inputValueReferences;
        refs[id] = e.target.value;
        this.setState({inputValueReferences: refs});
    }

    handleNotificationChange = (e, id, email, notificationType) => {
        let refs = this.state.checkboxReferences;
        refs[id] = e.currentTarget.checked;
        this.setState({checkboxReferences: refs});
        this.props.dispatch(updateNotificationPreference(email, notificationType, event.currentTarget.checked));
    }

    handleRowDeleteChange = (e, id) => {
        let indexToRemove = null;
        for(let i = 0; i < this.state.selectedRowIdsToDelete.length; i++) {
            if(this.state.selectedRowIdsToDelete[i] === id) {
                indexToRemove = i;
            }
        }
        if(indexToRemove !== null) {
            this.setState({
                selectedRowIdsToDelete: [
                    ...this.state.selectedRowIdsToDelete.slice(0, indexToRemove),
                    ...this.state.selectedRowIdsToDelete.slice(indexToRemove + 1)
                ]
            });
        } else {
            this.setState({
                selectedRowIdsToDelete: [...this.state.selectedRowIdsToDelete, id]
            });
        }
    }

    getHeader = () => {
        const headers = this.props.notificationEntries.length 
            ? this.props.notificationEntries[0]["notifications"]
            : defaultHeaders
        return (
            <DT.DataTableHead>
                <DT.DataTableRow>
                    <DT.DataTableHeadCell>Delete</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell>Email</DT.DataTableHeadCell>
                    {
                        headers.map(item => {
                            return (
                                <DT.DataTableHeadCell>{item.label}</DT.DataTableHeadCell>
                            );
                        })
                    }
                </DT.DataTableRow>
            </DT.DataTableHead>
        );
    }

    getBody = () => {
        const dataTableBody = this.props.notificationEntries.map((item, index) => {
            const rowId = item.pk
            const emailValue = this.state.inputValueReferences[rowId] === ""
                ? this.state.inputValueReferences[rowId]
                : this.state.inputValueReferences[rowId] || item.email;
            return (
                <DT.DataTableRow>
                    <DT.DataTableCell>
                        <Checkbox
                            checked={this.state.selectedRowIdsToDelete.includes(rowId)}
                            onChange={evt => this.handleRowDeleteChange(evt, rowId)} />
                    </DT.DataTableCell>
                    <DT.DataTableCell>
                        <TextField
                            onChange={(e) => this.handleEmailChange(e, item.pk)}
                            outlined={false} 
                            fullwidth={true} 
                            align="start" 
                            value={emailValue} />
                    </DT.DataTableCell>
                    {
                        item.notifications.map(notificationItem => {
                            const id = index.toString() + notificationItem.notification_type;
                            let checkboxSelection = notificationItem.is_active;
                            if(this.state.checkboxReferences[id] !== undefined && this.state.checkboxReferences[id] !== null) {
                                checkboxSelection = this.state.checkboxReferences[id]
                            }
                            return (
                                <DT.DataTableCell>
                                    <Checkbox 
                                        checked={checkboxSelection}
                                        onChange={evt => this.handleNotificationChange(evt, id, item.email, notificationItem.notification_type)} />
                                </DT.DataTableCell>
                            );
                        })
                    }
                </DT.DataTableRow>
            )
        });

        return (<DT.DataTableBody>{dataTableBody}</DT.DataTableBody>);
    }

    addNewRow = () => {
        let notifications = [];
        if(!this.props.notificationEntries.length) {
            notifications = defaultHeaders;
        } else {
            // use the first entry in notification entries as the template, since there may
            // new, unaccounted for columns
            notifications = this.props.notificationEntries[0].notifications.map(item => {
                item.is_active = false;
                return item;
            });
        }
        const rowTemplate = {
            pk: uuidv4(),
            email: "",
            notifications: notifications
        };
        this.props.dispatch(action.addNewNotificationRow(rowTemplate));
    }

    render() {
        return (
            <div>
                <div className="notification-action-bar-container">
                    <div className="notification-search-bar">
                        <TextField
                            icon="search"
                            trailingIcon="close"
                            label="Search" />
                    </div>
                    <div className="notification-button-container">
                        <Button
                            unelevated
                            label="Add New Row"
                            onClick={this.addNewRow} />
                        <div className="notification-spacer"></div>
                        <Button
                            danger
                            unelevated
                            label="Delete Selected"
                            disabled={!this.state.selectedRowIdsToDelete.length}
                            onClick={this.deleteRow} />
                    </div>
                </div>
                <DT.DataTable className="notification-data-table">
                    <DT.DataTableContent>
                        {this.getHeader()}
                        {this.getBody()}
                    </DT.DataTableContent>
                </DT.DataTable>
            </div>
        );
    }
}

const ConnectedNotifications = connect(state => ({
    notificationEntries: state.notifications.notificationEntries
}))(Notifications);

const notificationsElement = (
    <ConnectedComponentWrapper isVisible={true} pageTitle="NOTIFICATIONS">
        <ConnectedNotifications/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(notificationsElement, document.getElementById('master-container'));