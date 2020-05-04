import { api } from './network_client';

export function toggleNavigationDrawer() {
    return {
        type: "TOGGLE_NAVIGATION_DRAWER"
    }
}

export function selectMenuOption(selectedMenuName) {
    return {
        type: "SELECT_MENU_OPTION",
        selectedMenuName
    }
}

export function testGet() {
    return dispatch => {
        const testResponse = api.get('test', (data) => {
            console.warn("This is a success handler", data);
        }, (error) => {
            console.warn("This is an error handler", error);
        });
    }
}