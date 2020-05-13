import { api } from '../../static/js/network_client';

function updateFetchedNotifications(data) {
    return {
        type: 'UPDATE_FETCHED_NOTIFICATIONS',
        data
    }
}

export function getNotifications() {
    return dispatch => {
        api.get('notifications', (response) => {
            dispatch(updateFetchedNotifications(response.results.data));
        }, (error) => {
            console.warn(error);
        })
    }
}