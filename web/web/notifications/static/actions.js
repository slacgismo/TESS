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
    return (dispatch, getState) => {
        api.get('notifications', (response) => {
            const userId = getState().userSettings.userData.user_id
            const data = response.results.data.filter(v => v.created_by === userId);
            const convertedRes = groupDataBy(data, 'email');
            dispatch(updateFetchedNotifications(convertedRes));
        }, (error) => {
            console.warn(error);
        })
    }
}

export function postNotifications(data) {
    return dispatch => {
        api.post('notification', { json: { ...data } }, (response) => {
            dispatch(getNotifications());
        }, (error) => {
            console.warn(error);
        })
    }
}

export function updateNotifications(data) {
    return dispatch => {
        api.put('notification', { json: { ...data } }, (response) => {
            dispatch(getNotifications());
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
