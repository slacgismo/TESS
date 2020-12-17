import React from "react";
import { queue } from "./components/app_notification_queue";

export function createPopup(subject, description) {
    queue.notify({
        title: <b>{subject}</b>,
        body: description,
        dismissesOnAction: true,
        timeout: -1,
        actions: [{ title: "OK" }],
        open: true
    });
}

export function validateLoginData(
    username,
    password,
    usernameTitle,
    usernameBody,
    pwTitle,
    pwBody,
    isUserSettingsUpdate
) {
    let valid = true;
    if (!~username.indexOf("@")) {
        valid = false;
        createPopup(usernameTitle, usernameBody);
    }

    if (!isUserSettingsUpdate && password.length < 8) {
        valid = false;
        createPopup(pwTitle, pwBody);
    }

    if (isUserSettingsUpdate && 0 < password.length && password.length < 8) {
        valid = false;
        createPopup(pwTitle, pwBody);
    }

    return valid;
}
