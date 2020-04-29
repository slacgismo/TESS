import React from 'react';
import { connect } from 'react-redux';
import { List, ListItem } from '@rmwc/list';
import { Drawer, DrawerContent } from '@rmwc/drawer';

import '@rmwc/list/styles';
import '@rmwc/drawer/styles';

class NavigationDrawer extends React.Component {
    render() {
        return (
            <Drawer dismissible open={this.props.isDrawerOpen}>
                <DrawerContent>
                    <List>
                        <ListItem>Power Dispatch</ListItem>
                        <ListItem>Constraints</ListItem>
                        <ListItem>Markets</ListItem>
                        <ListItem>Cost Revenue</ListItem>
                        <ListItem>Alerts</ListItem>
                        <ListItem>Notifications</ListItem>
                        <ListItem>User Settings</ListItem>
                    </List>
                </DrawerContent>
            </Drawer>
        );
    }
}

export default connect(state => ({
    isDrawerOpen: state.drawerNavigationMenu.isDrawerOpen
}))(NavigationDrawer);