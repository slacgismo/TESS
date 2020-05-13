const initialState = {
    alertEntries: []
};

export default function alerts(state = initialState, action) {
    switch (action.type) {        
        case 'UPDATE_FETCHED_ALERTS':
            return { ...state, alertEntries: action.data }
        default:
            return state;
    }
}
