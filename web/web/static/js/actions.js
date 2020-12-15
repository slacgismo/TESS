import { api } from "./network_client";

export function completeLogout() {
    return {
        type: "USER_LOGGED_OUT",
        userLoggedOut: true,
    };
}

export function toggleNavigationDrawer() {
    return {
        type: "TOGGLE_NAVIGATION_DRAWER",
    };
}

export function selectMenuOption(selectedMenuName) {
    return {
        type: "SELECT_MENU_OPTION",
        selectedMenuName,
    };
}

// FIXME: DELETE LATER
// THIS IS HERE AS AN EXAMPLE ON HOW TO INTERACT WITH THE API CLIENT
export function getUtilities() {
    return (dispatch) => {
        const getUtilitiesRequest = api.get(
            "utilities",
            (data) => {
                console.warn("This is a success handler", data);
            },
            (error) => {
                console.warn("This is an error handler", error);
            }
        );
    };
}
export function postUtilities() {
    return (dispatch) => {
        const json = {
            json: {
                name: "test util",
                subscription_start: new Date().toISOString(),
                subscription_end: new Date().toISOString(),
            },
        };
        const postUtilitiesRequest = api.post(
            "utilities",
            json,
            (data) => {
                console.warn("This is a success handler", data);
            },
            (error) => {
                console.warn("This is an error handler", error);
            }
        );
    };
}
