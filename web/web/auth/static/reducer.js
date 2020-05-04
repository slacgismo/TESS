const initialState = {
    email: "",
    token: null
}

export default function auth(state = initialState, action) {
    switch (action.type) {        
        case "LOGIN_SUCCESSFUL":
            return { ...state, token: action.token }

        case "LOGIN_FAILED":
            return { ...state, token: null }
        default:
            return state
    }
}
