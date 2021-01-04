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
import { validateEmail } from "./helpers";

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
            selectedRowIdsToDelete: [],
            currentEmail: "",
            maxNotificationId: 0
        };
    }

    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption('notifications'));
        this.props.dispatch(action.getNotifications());
        this.props.dispatch(action.getAlertTypes());
    }

    update = (field, event) => {
        this.setState({ [field]: event.currentTarget.value });
    }

    handleEmailChange = (e, id) => {
        let refs = this.state.inputValueReferences;
        refs[id] = e.target.value;
        this.setState({inputValueReferences: refs});
    }

    handleNotificationChange = (e, id, notificationId, notExist, email, alertTypeId) => {
        let refs = this.state.checkboxReferences;
        refs[id] = e.currentTarget.checked;
        this.setState({checkboxReferences: refs});
        notExist
        ?
        this.props.dispatch(action.postNotifications({
            "alert_type_id" : alertTypeId,
            "email" : email,
            "is_active" : refs[id],
            "created_by" : 1
        }))
        :
        this.props.dispatch(action.updateNotifications({
            "notification_id" : notificationId,
            "alert_type_id" : alertTypeId,
            "email" : email,
            "is_active" : refs[id],
            "created_by" : 1
        }))
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
        const headers = this.props.alertTypeEntries.length
            ? this.props.alertTypeEntries
            : defaultHeaders
        return (
            <DT.DataTableHead>
                <DT.DataTableRow>
                    <DT.DataTableHeadCell>Delete</DT.DataTableHeadCell>
                    <DT.DataTableHeadCell>Email</DT.DataTableHeadCell>
                    {
                        headers.map(item => {
                            return (
                                <DT.DataTableHeadCell>{item.name}</DT.DataTableHeadCell>
                            );
                        })
                    }
                </DT.DataTableRow>
            </DT.DataTableHead>
        );
    }

    handleEmailAdd = (e) => {
        const isValid = validateEmail(e.target.value)
        const curEmail = this.state.currentEmail
        let update = false
        if (isValid) {
            this.props.notificationEntries.map((notificationEntry) => {
                // checking if email existed in the db
                if ((curEmail !== "") && (curEmail === notificationEntry.email)) {
                    update = true
                    notificationEntry.notifications.map((notification) => {
                        this.props.dispatch(action.updateNotifications({
                            "notification_id" : notification.notification_id,
                            "alert_type_id" : notification.alert_type_id,
                            "email" : e.target.value,
                            "created_by" : 1
                        }))
                    })
                }
            })
            if (!update) {
                this.props.dispatch(action.postNotifications({
                    "alert_type_id" : 1,
                    "email" : e.target.value,
                    "is_active" : "False",
                    "created_by" : 1
                }))
            }
        }
    }

    getBody = () => {
        let latestNotificationId = 0
        const numAlertTypes = this.props.alertTypeEntries.length
        const dataTableBody = this.props.notificationEntries.map((item, index) => {
            const numNotifications = item.notifications.length
            let alertTypes = []
            let notifications = []
            // create an array of unique alerttypeids
            this.props.alertTypeEntries.map((alertType) => {
                alertTypes.push(alertType.alert_type_id)
            })
            // add nonexistent alert types to data array being passed with a "non-existent" flag
            item.notifications.map((notification) => {
                if (alertTypes.includes(notification.alert_type_id)){
                    let index = alertTypes.indexOf(notification.alert_type_id)
                    alertTypes.splice(index, 1)
                }
                if (notification.notification_id > latestNotificationId) {
                    latestNotificationId = notification.notification_id
                }
                notifications.push(notification)
            })
            // create nonexistent notifications in
            alertTypes.map((alertType) => {
                notifications.push({
                    "alert_type_id" : alertType,
                    "is_active" : false,
                    "notification_id" : latestNotificationId + 1,
                    "not_exist" : true
                })
                latestNotificationId++
            })
            // sorting items
            notifications.sort((a, b) => (a.alert_type_id > b.alert_type_id) ? 1 : -1)
            const rowId = notifications[0].notification_id
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
                            onChange={(e) => this.handleEmailChange(e, rowId)}
                            onBlur={(e) => this.handleEmailAdd(e)}
                            onFocus={(e) => this.update("currentEmail", e)}
                            outlined={false}
                            fullwidth={true}
                            align="start"
                            value={emailValue} />
                    </DT.DataTableCell>
                    {
                        notifications.map(notificationItem => {
                            const id = index.toString() + notificationItem.notification_id;
                            let checkboxSelection = notificationItem.is_active;
                            if(this.state.checkboxReferences[id] !== undefined && this.state.checkboxReferences[id] !== null) {
                                checkboxSelection = this.state.checkboxReferences[id]
                            }
                            return (
                                <DT.DataTableCell>
                                    <Checkbox
                                        checked={checkboxSelection}
                                        onChange={e => this.handleNotificationChange(e, id, notificationItem.notification_id, notificationItem.not_exist, item.email, notificationItem.alert_type_id)} />
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
        let currentId = this.state.maxNotificationId
        let notifications = [];
        if(!this.props.alertTypeEntries.length) {
            notifications = defaultHeaders;
        } else {
            // use the first entry in notification entries as the template, since there may
            // new, unaccounted for columns
            notifications = this.props.notificationEntries[0].notifications.map(item => {
                currentId++
                return {
                    alert_type_id: item.alert_type_id,
                    is_active: false,
                    notification_id: uuidv4()
                }
            });
        }
        const rowTemplate = {
            email: "",
            notifications: notifications
        }
        this.props.dispatch(action.addNewNotificationRow(rowTemplate))
    }

    deleteRow = () => {
        this.props.notificationEntries.map((notificationEntry) => {
            let notificationIds = notificationEntry.notifications.map((notification) => {
                return notification.notification_id
            })
            this.state.selectedRowIdsToDelete.map((rowId) => {
                if (notificationIds.includes(rowId)){
                    notificationIds.map((notificationId) => {
                        this.props.dispatch(action.deleteNotifications({notification_id : notificationId}));
                    })
                }

            })
        })
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
    notificationEntries: state.notifications.notificationEntries,
    alertTypeEntries: state.notifications.alertTypeEntries
}))(Notifications);

const notificationsElement = (
    <ConnectedComponentWrapper isVisible={true} pageTitle="NOTIFICATIONS">
        <ConnectedNotifications/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(notificationsElement, document.getElementById('master-container'));
