import { api } from '../../static/js/network_client';

// helper functions to group data for frontend
const groupBy = (array, key) =>
  array.reduce((result, { [key]: k, ...rest }) => {
    (result[k] = result[k] || []).push(rest);
    return result;
  }, {});

const groupDataBy = (array, key) =>
  Object.entries(groupBy(array, key)).map(([email, notifications]) => ({
    email,
    notifications
  })
);

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
            const convertedRes = groupDataBy(response.results.data, 'email');
            dispatch(updateFetchedNotifications(convertedRes));
        }, (error) => {
            console.warn(error);
        })
    }
}

function updateFetchedAlertTypes(data) {
  return {
      type: 'UPDATE_FETCHED_ALERT_TYPES',
      data
  }
}

export function getAlertTypes() {
  return dispatch => {
    api.get('alert_types', (response) => {
        dispatch(updateFetchedAlertTypes(response.results.data));
    }, (error) => {
        console.warn(error)
    })
  }
}