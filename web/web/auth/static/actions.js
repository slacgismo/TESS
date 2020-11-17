import { api } from "../../static/js/network_client";
import { menuRoutes } from '../../static/js/config/routes';

export function loginSuccessful(token) {
    window.location.href = menuRoutes[0].path;
    return {
        type: "LOGIN_SUCCESSFUL",
        token
    }
}

export function loginFailed(token) {
    return {
        type: "LOGIN_FAILED",
        token
    }
}

export function processLogin(username, password) {
    return dispatch => {      
        const json = {
            json: {
                username: username,
                password_hash: password
            }
        }
        api.post("validate_login", json, (data) => {
            console.warn("This is a success handler", data);
            dispatch(loginSuccessful);
        }, (error) => {
            console.warn("This is an error handler", error);
            dispatch(loginFailed);
        });
    }
}

export function processSignUp(username, firstName, lastName, password) {
    return dispatch => {
        try {
            // Placeholders for address_id and utility_id
            const userJson = {
                json: {
                    email: username,
                    first_name: firstName,
                    last_name: lastName,
                    address_id: "1",
                    utility_id: "1"
                }
            }
            api.post("user", userJson, (data) => {
                const userId = data.results.data.id.toString()
                const loginJson = {
                    json: {
                        username: username,
                        password_hash: password,
                        user_id: userId
                    }
                }
                api.post("create_login", loginJson, (data) => {
                    dispatch(loginSuccessful);
                }, (error) => {
                    console.warn("This is an error handler", error);
                    dispatch(loginFailed);
                })
            }, (error) => {
                console.warn("This is an error handler", error);
                dispatch(loginFailed);
            })
        }
        catch(error) {
            console.warn("This is an error handler", error);
            dispatch(loginFailed);
        }
    }
}
