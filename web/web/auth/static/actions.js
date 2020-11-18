import { api } from "../../static/js/network_client";
import { menuRoutes } from "../../static/js/config/routes";
import { createLoginError } from "./helpers";

export function loginSuccessful(token) {
    window.location.href = menuRoutes[0].path;
    return {
        type: "LOGIN_SUCCESSFUL",
        token,
    };
}

export function loginFailed(token) {
    return {
        type: "LOGIN_FAILED",
        token,
    };
}

export function processLogin(username, password) {
    return (dispatch) => {
        const json = {
            json: {
                username: username,
                password_hash: password,
            },
        };
        api.post(
            "validate_login",
            json,
            (data) => {
                dispatch(loginSuccessful);
            },
            (error) => {
                createLoginError(
                    "Login failed",
                    "Incorrect username and/or password"
                );
                dispatch(loginFailed);
            }
        );
    };
}

export function processSignUp(username, firstName, lastName, password) {
    return (dispatch) => {
        try {
            // Placeholders for address_id and utility_id
            const userJson = {
                json: {
                    email: username,
                    first_name: firstName,
                    last_name: lastName,
                    address_id: "1",
                    utility_id: "1",
                },
            };
            api.post(
                "user",
                userJson,
                (data) => {
                    const userId = data.results.data.id.toString();
                    const loginJson = {
                        json: {
                            username: username,
                            password_hash: password,
                            user_id: userId,
                        },
                    };
                    api.post(
                        "create_login",
                        loginJson,
                        (data) => {
                            dispatch(loginSuccessful);
                        },
                        (error) => {
                            createLoginError(
                                "Sign up failed",
                                "Email already in use"
                            );
                            dispatch(loginFailed);
                        }
                    );
                },
                (error) => {
                    createLoginError("Sign up failed", "Email already in use");
                    dispatch(loginFailed);
                }
            );
        } catch (error) {
            createLoginError("Server error", "Something went wrong");
            dispatch(loginFailed);
        }
    };
}
