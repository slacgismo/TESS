import { api } from '../../static/js/network_client';

const groupBy = (array, key) => {
    return array.reduce((result, currentValue) => {
      (result[currentValue[key]] = result[currentValue[key]] || []).push(
        currentValue
      );
      return result;
    }, {}); 
  };


function updateFetchedNotifications(data) {
    return {
        type: 'UPDATE_FETCHED_NOTIFICATIONS',
        data
    }
}

export function addNewNotificationRow(rowTemplate) {
    return { 
        type: 'ADD_NEW_NOTIFICATION_ROW',
        rowTemplate
    }
}

export function getNotifications() {
    return dispatch => {
        api.get('notifications', (response) => {
            const groupedByEmail = groupBy(response.results.data, "email");
            dispatch(updateFetchedNotifications(groupedByEmail));
        }, (error) => {
            console.warn(error);
        })
    }
}