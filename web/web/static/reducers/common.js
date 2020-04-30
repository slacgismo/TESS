import { combineReducers } from "redux";
import auth from '../../auth/static/reducer';
import drawerNavigationMenu from './navigation_drawer_reducer';
import alerts from '../../alerts/static/reducer';
import markets from '../../markets/static/reducer';
import constraints from '../../constraints/static/reducer';
import costRevenue from '../../cost_revenue/static/reducer';
import userSettings from '../../user_settings/static/reducer';
import notifications from '../../notifications/static/reducer';
import { storage, capacity } from '../../power_dispatch/static/reducer';

const appReducer = combineReducers({
    auth,
    alerts,
    markets,
    constraints,
    costRevenue,
    notifications,
    storage,
    capacity,
    userSettings,
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
