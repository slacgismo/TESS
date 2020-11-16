import { api } from '../../static/js/network_client';

export function loginSuccessful(token) {
    return {
        type: "LOGIN_SUCCESSFUL",
        token
    }
}
