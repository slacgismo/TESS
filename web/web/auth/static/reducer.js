const initialState = {
    userData: {},
    userLoggedIn: false
};

export default function auth(state = initialState, action) {
    switch (action.type) {
        case "LOGIN_SUCCESSFUL":
        case "LOGIN_FAILED":
            return {
                ...state,
                userLoggedIn: action.userLoggedIn,
                userData: action.userData,
            };
        case "UPDATE_USER_DATA":
            return { ...state, userData: action.userData };
        case "RESET_USER_LOGGED_IN":
            return { ...state, userLoggedIn: action.userLoggedIn };
        default:
            return state;
    }
}
