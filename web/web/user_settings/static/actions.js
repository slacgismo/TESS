import { createErrorMessage } from "../../static/js/helpers"
import { api } from "../../static/js/network_client";

export function updateSuccessful() {
    return {
        type: "UPDATE_SUCCESSFUL",
    };
}

export function updateFailed() {
    return {
        type: "UPDATE_FAILED",
    };
}

export function updateUserSettings(userId, username, password, firstName, lastName) {
    return (dispatch) => {
        try {
            const userData = {
                "user": {
                    "id": userId,
                    "first_name": firstName,
                    "last_name": lastName,
                },
                "login": {
                    "username": username,
                    "password_hash": password,
                }
            };
            api.patch(
                "update_user_settings",
                { json: { ...userData } },
                (data) => {
                    dispatch(updateSuccessful());
                    createErrorMessage(
                        "",
                        "User settings have been successfully updated"
                    );
                },
                (error) => {
                    createErrorMessage(
                        "Failed",
                        "Unable to update user settings"
                    );
                    dispatch(updateFailed());
                }
            );
        } catch (error) {
            createErrorMessage("Server error", "Something went wrong");
            dispatch(updateFailed());
        }
    };
}