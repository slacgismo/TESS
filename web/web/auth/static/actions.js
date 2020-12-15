import { api } from "../../static/js/network_client";
import { createPopup } from "../../static/js/helpers";

export function loginSuccessful(userData) {
    return {
        type: "LOGIN_SUCCESSFUL",
        userLoggedIn: true,
        userData: userData,
    };
}

export function loginFailed() {
    return {
        type: "LOGIN_FAILED",
        userLoggedIn: false,
        userData: {},
    };
}

export function resetUserLoggedIn() {
    return {
        type: "RESET_USER_LOGGED_IN",
        userLoggedIn: false,
    };
}

export function updateUserData(userData) {
    return {
        type: "UPDATE_USER_DATA",
        userData: userData,
    };
}

export function processLogin(username, password) {
    return (dispatch) => {
        try {
            const loginData = {
                username: username,
                password_hash: password,
            };
            api.post(
                "login",
                { json: { ...loginData } },
                (data) => {
                    dispatch(loginSuccessful(data.results.data.login));
                },
                (error) => {
                    createPopup(
                        "Login failed",
                        "Incorrect username and/or password"
                    );
                    dispatch(loginFailed());
                }
            );
        } catch (error) {
            createPopup("Server error", "Something went wrong");
            dispatch(loginFailed());
        }
    };
}

export function processSignUp(username, firstName, lastName, password) {
    return (dispatch) => {
        try {
            // Placeholders for address_id and utility_id
            const signUpData = {
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
            };
            api.post(
                "sign_up",
                { json: { ...signUpData } },
                (data) => {
                    dispatch(loginSuccessful(data.results.data.login));
                },
                (error) => {
                    createPopup("Sign up failed", "Email already in use");
                    dispatch(loginFailed());
                }
            );
        } catch (error) {
            createPopup("Server error", "Something went wrong");
            dispatch(loginFailed());
        }
    };
}
