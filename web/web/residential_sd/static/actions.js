import { api } from '../../static/js/network_client';

export function getPVSystemData() {
    return dispatch => {
        api.get('power/system_load/?is_capacity=true', (response) => {
            dispatch(capacitySystemLoadDataUpdated(response.results.data));
        }, (error) => {
            console.warn(error);
        });
    };
}
