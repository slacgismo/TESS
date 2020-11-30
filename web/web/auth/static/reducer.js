const initialState = {
    email: "",
    userLoggedIn: false
}

export default function auth(state = initialState, action) {
    switch (action.type) {        
        case "LOGIN_SUCCESSFUL":
        case "LOGIN_FAILED":
        case "RESET_USER_LOGGED_IN":
            return { ...state, userLoggedIn: action.userLoggedIn }
        default:
            return state
    }
}
