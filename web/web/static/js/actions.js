import Cookies from "js-cookie";
import { api } from "./network_client";
import { createErrorMessage } from "./helpers";

export function completeLogout() {
    return {
        type: "USER_LOGGED_OUT",
        userLoggedOut: true,
    };
}

export function resetUserLoggedOut() {
    return {
        type: "RESET_USER_LOGGED_OUT",
        userLoggedOut: false,
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

export function logout() {
    return (dispatch) => {
        try {
            const accessTokenJson = {
                headers: {
                    Authorization: "Bearer " + Cookies.get("access_token"),
                },
            };
            api.delete(
                "logout",
                accessTokenJson,
                () => {
                    Cookies.remove("access_token");
                    Cookies.remove("refresh_token");
                    window.location.href = "/";
                    dispatch(completeLogout);
                },
                (error) => {
                    createErrorMessage("Error", "Unable to log out");
                }
            );
        } catch (error) {
            createErrorMessage("Server error", "Something went wrong");
        }
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
