/**
 * SLAC 2020
 *
 * Created by: jongon
 *
 * Action creators for the commonalities across the entire application
 */

import { globalPersistor, navRef } from '../app'

export function hideModal() {
    return {
        type: 'HIDE_MODAL'
    }
}

export function clearStateCache() {
    return dispatch => {
        dispatch({ type: 'CLEAR_ENTIRE_STATE' })
        globalPersistor.flush()
    }
}

export function signout() {
    return dispatch => {
        dispatch(hideModal())
        dispatch(clearStateCache())
        _navigatorFacility('LandingPage')        
        api.setAuthToken(null)       
    }
}

function _navigatorFacility(pageName) {
    navRef.dispatch(NavigationActions.navigate({routeName: pageName}))
}

export function navigatorFacility(pageName) {
    return dispatch => { _navigatorFacility(pageName) }
}
