import { api } from '../../static/js/network_client';

export function getCapacitySystemLoadData() {
    return dispatch => {
        api.get('power/system_load/?is_capacity=true', (response) => {
            dispatch(capacitySystemLoadDataUpdated(response.results.data));
        }, (error) => {
            console.warn(error);
        });
    };
}

export function getStorageSystemLoadData() {
    return dispatch => {
        api.get('power/system_load/?is_storage=true', (response) => {
            dispatch(storageSystemLoadDataUpdated(response.results.data));
        }, (error) => {
            console.warn(error);
        });
    };
}

export function capacitySystemLoadDataUpdated(data) {
    return {
        type: 'CAPACITY_SYSTEM_LOAD_DATA_UPDATED',
        data
    };
}

export function storageSystemLoadDataUpdated(data) {
    return {
        type: 'STORAGE_SYSTEM_LOAD_DATA_UPDATED',
        data
    };
}

export function getResourcesData() {
    return dispatch => {
        api.get('power/resources', (response) => {
            dispatch(capacityResourcesDataUpdated(response.results.data));
        }, (error) => {
            console.warn(error);
        });
    }
}

export function capacityResourcesDataUpdated(data) {
    return {
        type: 'CAPACITY_RESOURCES_DATA_UPDATED',
        data
    };
}