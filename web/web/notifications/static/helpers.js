import React from "react";
import { queue } from "../../static/js/components/app_notification_queue";

export function validateEmail(email) {
    let valid = true;
    if (!~email.indexOf("@")) {
        valid = false;
        // validate the email contains at least an @ symbol
        queue.notify({
            title: <b>email</b>,
            body:
                'Must be a valid email in the format: "someone@somewhere.com"',
            dismissesOnAction: true,
            timeout: -1,
            actions: [{ title: "Dismiss" }],
        });
    }
    return valid;
}
