import React from "react";
import { queue } from "../../static/js/components/app_notification_queue";

export function createLoginError(subject, description) {
    queue.notify({
        title: <b>{subject}</b>,
        body: description,
        dismissesOnAction: true,
        timeout: -1,
        actions: [{ title: "Dismiss" }],
    });
}

export function validateLogin(username, password) {
    let valid = true;
    if (!~username.indexOf("@")) {
        valid = false;
        // validate the email contains at least an @ symbol
        queue.notify({
            title: <b>Username</b>,
            body:
                'Must be a valid email in the format: "someone@somewhere.com"',
            dismissesOnAction: true,
            timeout: -1,
            actions: [{ title: "Dismiss" }],
        });
    }

    if (password.length < 8) {
        valid = false;
        // validate the password is at least eight chars long
        // validate the username is not empty
        queue.notify({
            title: <b>Password</b>,
            body: "Must be at least 8 characters long",
            dismissesOnAction: true,
            timeout: -1,
            actions: [{ title: "Dismiss" }],
        });
    }
    return valid;
}
