const initialState = {
    userData: {},
    userLoggedIn: false,
    userLoggedOut: false
}

export default function auth(state = initialState, action) {
    switch (action.type) {        
        case "LOGIN_SUCCESSFUL":
        case "LOGIN_FAILED":
            return { ...state, userLoggedIn: action.userLoggedIn, userData: action.userData }
        case "RESET_USER_LOGGED_IN":
            return { ...state, userLoggedIn: action.userLoggedIn }
        case "USER_LOGGED_OUT":
            return { ...state, userLoggedOut: action.userLoggedOut }
        case "EMPTY_USER_DATA":
            return { ...state, userData: action.userData }
        default:
            return state
    }
}
