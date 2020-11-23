const initialState = {
    email: "",
    userLoggedIn: false
}

export default function auth(state = initialState, action) {
    switch (action.type) {        
        case "LOGIN_SUCCESSFUL":
            return { ...state, userLoggedIn: action.userLoggedIn }
        case "LOGIN_FAILED":
            return { ...state, userLoggedIn: action.userLoggedIn }
        case "RESET_USER_LOGGED_IN":
            return { ...state, userLoggedIn: action.userLoggedIn }
        default:
            return state
    }
}
