import { api } from '../../static/js/network_client';

export function getSystemLoadData() {
    return dispatch => {
        api.get('power/system_load', (response) => {
            dispatch(systemLoadDataUpdated(response.results.data));
        }, (error) => {
            console.warn(error);
        });
    };
}

export function systemLoadDataUpdated(data) {
    return {
        type: 'SYSTEM_LOAD_DATA_UPDATED',
        data
    };
}

export function getResourcesData() {
    return dispatch => {
        api.get('power/resources', (response) => {
            dispatch(resourcesDataUpdated(response.results.data));
        }, (error) => {
            console.warn(error);
        });
    }
}

export function resourcesDataUpdated(data) {
    return {
        type: 'RESOURCES_DATA_UPDATED',
        data
    };
}