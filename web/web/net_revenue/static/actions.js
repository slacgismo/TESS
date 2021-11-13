import { api } from '../../static/js/network_client';

// Auction Market Chart
export function getCashFlowData() {
    return dispatch => {
        api.get('net_revenue/cash_flow', (response) => {
            dispatch(cashFlowDataUpdated(response.results.data));
        }, (error) => {
            console.warn(error);
        });
    };
}

export function cashFlowDataUpdated(data) {
    return {
        type: 'CASH_FLOW_DATA_UPDATED',
        data
    };
}
