const initialState = {
    userData: {},
};

export default function userSettings(state = initialState, action) {
    switch (action.type) {
        case "LOGIN_SUCCESSFUL":
            return { ...state, userData: action.userData };
        case "UPDATE_SUCCESSFUL":
        case "UPDATE_FAILED":
            return {
                ...state,
            };
        default:
            return state;
    }
}
