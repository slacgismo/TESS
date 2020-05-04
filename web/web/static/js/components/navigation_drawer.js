import React from 'react';
import { connect } from 'react-redux';
import { List, SimpleListItem } from '@rmwc/list';
import { Drawer, DrawerContent } from '@rmwc/drawer';
import { selectMenuOption, toggleNavigationDrawer } from '../actions';

import '@rmwc/list/styles';
import '@rmwc/drawer/styles';

class NavigationDrawer extends React.Component {
    constructor(props) {
        super(props);
        this.menuOptions = [
            {
                id: 'power-dispatch',
                label: 'Power Dispatch',
                path: '/power'
            },
            {
                id: 'constraints',
                label: 'Constraints',
                path: '/constraints'
            },
            {
                id: 'markets',
                label: 'Markets',
                path: '/markets'
            },
            {
                id: 'cost-revenue',
                label: 'Cost Revenue',
                path: '/cost_revenue'
            },
            {
                id: 'alerts',
                label: 'Alerts',
                path: '/alerts'
            },
            {
                id: 'notifications',
                label: 'Notifications',
                path: '/notifications'
            },
            {
                id: 'user-settings',
                label: 'User Settings',
                path: '/user_settings'
            }
        ];
    }

    onClick = (path, id) => {
        this.props.dispatch(toggleNavigationDrawer());
        this.props.dispatch(selectMenuOption(id));
        window.location.href = path;
    }

    generateMenuOptions = () => {
        return this.menuOptions.map(item => {
            return (
                <SimpleListItem 
                    selected={item.id === this.props.selectedMenuName}
                    onClick={() => this.onClick(item.path, item.id)}>
                    {item.label}
                </SimpleListItem>
            );
        })
    }

    render() {
        if(!this.props.isVisible) {
            return null;
        }
        
        return (
            <Drawer dismissible open={this.props.isDrawerOpen}>
                <DrawerContent>
                    <List>
                        {this.generateMenuOptions()}
                    </List>
                </DrawerContent>
            </Drawer>
        );
    }
}

export default connect(state => ({
    isDrawerOpen: state.drawerNavigationMenu.isDrawerOpen,
    selectedMenuName: state.drawerNavigationMenu.selectedMenuName
}))(NavigationDrawer);