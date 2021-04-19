const initialState = {
    supplyData: [],
    demandData: []
}

// need to be tested when backend for residential-sd is implemented
export default function residentialSD(state = initialState, action) {
    switch (action.type) {
        case 'DAILY_ENERGY_SUPPLY_UPDATED':
            return { ...state, supplyData: action.data };

        case 'DAILY_ENERGY_DEMAND_UPDATED':
            return { ...state, demandData: action.data };

        default:
            return state;
    }
}
