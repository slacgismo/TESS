import React from 'react';
import { connect } from 'react-redux';
import { menuRoutes } from '../config/routes';
import { List, SimpleListItem } from '@rmwc/list';
import { Drawer, DrawerContent } from '@rmwc/drawer';
import { selectMenuOption, toggleNavigationDrawer } from '../actions';
import Cookies from "js-cookie";

import '@rmwc/list/styles';
import '@rmwc/drawer/styles';

class NavigationDrawer extends React.Component {
    constructor(props) {
        super(props);
        this.menuOptions = menuRoutes;
    }

    onClick = (path, id) => {
        this.props.dispatch(toggleNavigationDrawer());
        this.props.dispatch(selectMenuOption(id));
        window.location.href = `${path}?jwt=${Cookies.get("access_token")}`;
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