const initialState = {
    auctionMarketData: [],
    clearingPriceData: [],
    energyDemandData: [],
}

export default function markets(state = initialState, action) {
    switch (action.type) {
        case 'AUCTION_MARKET_DATA_UPDATED':
            return { ...state, auctionMarketData: action.data };
        case 'CLEARING_PRICE_DATA_UPDATED':
            return { ...state, clearingPriceData: action.data };
        case 'ENERGY_DEMAND_DATA_UPDATED':
            return { ...state, energyDemandData: action.data };
        default:
            return state;
    }
}
