import { api } from '../../static/js/network_client';

// Auction Market Chart
export function getAuctionMarketData() {
    return dispatch => {
        api.get('markets/auction_market', (response) => {
            dispatch(auctionMarketDataUpdated(response.results.data));
        }, (error) => {
            console.warn(error);
        });
    };
}

export function auctionMarketDataUpdated(data) {
    return {
        type: 'AUCTION_MARKET_DATA_UPDATED',
        data
    };
}


// Clearing Price Over Time
export function getClearingPriceData() {
    return dispatch => {
        api.get('markets/clearing_price', (response) => {
            dispatch(ClearingPriceDataUpdated(response.results.data));
        }, (error) => {
            console.warn(error);
        });
    };
}

export function ClearingPriceDataUpdated(data) {
    return {
        type: 'CLEARING_PRICE_DATA_UPDATED',
        data
    };
}


// Energy Demand Data
export function getEnergyDemandData() {
    return dispatch => {
        api.get('markets/energy_demand', (response) => {
            dispatch(EnergyDemandDataUpdated(response.results.data));
        }, (error) => {
            console.warn(error);
        });
    };
}

export function EnergyDemandDataUpdated(data) {
    return {
        type: 'ENERGY_DEMAND_DATA_UPDATED',
        data
    };
}
