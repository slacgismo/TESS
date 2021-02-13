import { api } from '../../static/js/network_client';
import { createPopup } from '../../static/js/helpers';

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
            createPopup('Check API connection')
        })
    }
}

export function updateAlerts(data) {
    return dispatch => {
        api.put('alert', { json: { ...data } }, (response) => {
            dispatch(getAlerts());
        }, (error) => {
            createPopup('Check API connection')
        })
    }
}
