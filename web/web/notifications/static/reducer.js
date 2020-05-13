const initialState = {
    notificationEntries: []
}

export default function notifications(state = initialState, action) {
    switch (action.type) {
        case 'UPDATE_FETCHED_NOTIFICATIONS':
            return { ...state, notificationEntries: action.data }
        default:
            return state;
    }
}
