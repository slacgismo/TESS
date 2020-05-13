import { api } from '../../static/js/network_client';

function updateFetchedAlerts(data) {
    return {
        type: 'UPDATE_FETCHED_ALERTS',
        data
    }
}

export function getAlerts() {
    return dispatch => {
        api.get('alerts', (response) => {
            dispatch(updateFetchedAlerts(response.results.data));
        }, (error) => {
            console.warn(error);
        })
    }
}