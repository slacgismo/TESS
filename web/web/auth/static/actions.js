import Cookies from "js-cookie";
import { api } from "../../static/js/network_client";
import { createLoginError } from "./helpers";

export function loginSuccessful() {
    return {
        type: "LOGIN_SUCCESSFUL",
        userLoggedIn: true,
    };
}

export function loginFailed() {
    return {
        type: "LOGIN_FAILED",
        userLoggedIn: false,
    };
}

export function resetUserLoggedIn() {
    return {
        type: "RESET_USER_LOGGED_IN",
        userLoggedIn: false,
    };
}

export function processLogin(username, password) {
    return (dispatch) => {
        try {
            const json = {
                json: {
                    username: username,
                    password_hash: password,
                },
            };
            api.post(
                "login",
                json,
                (data) => {
                    Cookies.set("access_token", data.results.data.access_token);
                    Cookies.set("refresh_token", data.results.data.refresh_token);
                    dispatch(loginSuccessful());
                },
                (error) => {
                    console.warn(error);
                    createLoginError(
                        "Login failed",
                        "Incorrect username and/or password"
                    );
                    dispatch(loginFailed());
                }
            );
        } catch (error) {
            createLoginError("Server error", "Something went wrong");
            dispatch(loginFailed());
        }
    };
}

export function processSignUp(username, firstName, lastName, password) {
    return (dispatch) => {
        try {
            // Placeholders for address_id and utility_id
            const json = {
                json: {
                    user: {
                        email: username,
                        first_name: firstName,
                        last_name: lastName,
                        address_id: "1",
                        utility_id: "1",
                        is_active: true,
                    },
                    login: {
                        username: username,
                        password_hash: password,
                    },
                },
            };
            api.post(
                "sign_up",
                json,
                (data) => {
                    console.log(data.results.data.access_token)
                    Cookies.set("access_token", data.results.data.access_token);
                    Cookies.set(
                        "refresh_token",
                        data.results.data.refresh_token
                    );
                    dispatch(loginSuccessful());
                },
                (error) => {
                    createLoginError("Sign up failed", "Email already in use");
                    dispatch(loginFailed());
                }
            );
        } catch (error) {
            createLoginError("Server error", "Something went wrong");
            dispatch(loginFailed());
        }
    };
}
