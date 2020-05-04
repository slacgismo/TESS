export function loginSuccessful(token) {
    return {
        type: "LOGIN_SUCCESSFUL",
        token
    }
}