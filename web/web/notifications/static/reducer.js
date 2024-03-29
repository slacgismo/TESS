const initialState = {
    notificationEntries: [],
    alertTypeEntries: []
}

export default function notifications(state = initialState, action) {
    switch (action.type) {
        case 'UPDATE_FETCHED_NOTIFICATIONS':
            return { ...state, notificationEntries: action.data };

        case 'ADD_NEW_NOTIFICATION_ROW':
            state.notificationEntries.unshift(action.rowTemplate);
            return { ...state, notificationEntries: state.notificationEntries.slice(0) };

        case 'UPDATE_FETCHED_ALERT_TYPES':
            return { ...state, alertTypeEntries: action.data };

        default:
            return state;
    }
}
