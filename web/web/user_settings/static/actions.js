import { createPopup } from "../../static/js/helpers";
import { api } from "../../static/js/network_client";
import { updateUserData } from "../../auth/static/actions";

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

export function updateUserSettings(
    userId,
    username,
    password,
    firstName,
    lastName
) {
    return (dispatch) => {
        try {
            const userData = {
                user: {
                    id: userId,
                    first_name: firstName,
                    last_name: lastName,
                },
                login: {
                    username: username,
                    password_hash: password,
                },
            };
            api.patch(
                "update_user_settings",
                { json: { ...userData } },
                (data) => {
                    console.log("HEYYYY")
                    console.log(data)
                    dispatch(updateUserData(data.results.data));
                    createPopup(
                        "",
                        "User settings have been successfully updated"
                    );
                },
                (error) => {
                    createPopup(
                        "Failed",
                        "Unable to update user settings"
                    );
                    dispatch(updateFailed());
                }
            );
        } catch (error) {
            createPopup("Server error", "Something went wrong");
            dispatch(updateFailed());
        }
    };
}
