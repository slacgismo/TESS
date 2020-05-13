import React from 'react';
import ReactDOM from 'react-dom';
import * as action from './actions';
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
    { "label": "Yellow Alarm (Load)" },
    { "label": "Telecomm Alerts" },
    { "label": "Red Alarm (Load)" },
    { "label": "Red Alarm (Price)" },
    { "label": "Yellow Alarm (Price)" },
    { "label": "Capacity Bounds" },
    { "label": "Resource Depletion" },
    { "label": "Price Alerts" }
]

class Notifications extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            checkboxReferences: {}
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

    handleChange = (e, id, email, notificationType) => {
        let refs = this.state.checkboxReferences;
        refs[id] = e.currentTarget.checked;
        this.setState({checkboxReferences: refs});
        //this.props.dispatch(updateNotificationPreference(email, notificationType, event.currentTarget.checked));
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
            return (
                <DT.DataTableRow>
                    <DT.DataTableCell>
                        <Checkbox />
                    </DT.DataTableCell>
                    <DT.DataTableCell>{item.email}</DT.DataTableCell>
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
                                        onChange={evt => this.handleChange(evt, id, item.email, notificationItem.notification_type)} />
                                </DT.DataTableCell>
                            );
                        })
                    }
                </DT.DataTableRow>
            )
        });

        return (<DT.DataTableBody>{dataTableBody}</DT.DataTableBody>);
    }

    render() {
        return (
            <div>
                <div className="notification-action-bar-container">
                    <div className="notification-search-bar">
                        <TextField fullwidth icon="search" trailingIcon="close" label="Search" />
                    </div>
                    <div className="notification-button-container">
                        <Button label="Add New Row" unelevated />
                        <div className="notification-spacer"></div>
                        <Button danger label="Delete Selected" unelevated disabled={true} />
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
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedNotifications/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(notificationsElement, document.getElementById('master-container'));