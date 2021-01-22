import React from 'react';
import { createPopup } from '../../static/js/helpers'

export function validateEmail(email) {
    let valid = true;
    if (!~email.indexOf("@")) {
        valid = false;
        // validate the email contains at least an @ symbol
        createPopup('Must be a valid email in the format: "someone@somewhere.com"', email)
    }
    return valid;
}
