const initialState = {
    cashFlowData: [],
}

export default function netRevenue(state = initialState, action) {
    switch (action.type) {
        case 'CASH_FLOW_DATA_UPDATED':
            return { ...state, cashFlowData: action.data };
        default:
            return state;
    }
}
