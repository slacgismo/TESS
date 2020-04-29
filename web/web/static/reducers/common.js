import { combineReducers } from "redux";
import auth from '../../auth/static/reducer';
import drawerNavigationMenu from './navigation_drawer_reducer';

const appReducer = combineReducers({
    auth,
    drawerNavigationMenu
})

// Reset to initial state when logging out.
const baseReducer = (state, action) => {
    if (action.type === "LOGOUT") {
        //destroySession()
        state = undefined
    }
    return appReducer(state, action)
}

export default baseReducer
