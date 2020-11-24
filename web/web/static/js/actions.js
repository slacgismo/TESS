import Cookies from "js-cookie";
import { api, auth } from "./network_client";
import { createError } from "./helpers";

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
            const access_token = Cookies.get("access_token");
            const access_token_json = {
                headers: {
                    Authorization: "Bearer " + access_token,
                },
            };
            auth.delete(
                "access_revoke",
                access_token_json,
                () => {
                    Cookies.remove("access_token");
                    const refresh_token = Cookies.get("refresh_token");
                    const refresh_token_json = {
                        headers: {
                            Authorization: "Bearer " + refresh_token,
                        },
                    };
                    auth.delete(
                        "refresh_revoke",
                        refresh_token_json,
                        () => {
                            Cookies.remove("refresh_token");
                            window.location.href = "/";
                            dispatch(completeLogout);
                            createError(
                                "",
                                "You have successfully logged out."
                            );
                        },
                        (error) => {
                            createError("Error", "Unable to log out");
                        }
                    );
                },
                (error) => {
                    createError("Error", "Unable to log out");
                }
            );
        } catch (error) {
            createError("Server error", "Something went wrong");
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
