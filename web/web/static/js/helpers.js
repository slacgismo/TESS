import React from "react";
import { queue } from "./components/app_notification_queue";

export function createError(subject, description) {
    queue.notify({
        title: <b>{subject}</b>,
        body: description,
        dismissesOnAction: true,
        timeout: -1,
        actions: [{ title: "Dismiss" }],
    });
}
