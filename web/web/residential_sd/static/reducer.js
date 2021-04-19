const initialState = {
    supplyData: [],
    demandData: []
}

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
