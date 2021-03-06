import { combineReducers } from "redux";
import auth from "../../../auth/static/reducer";
import drawerNavigationMenu from "../reducers";
import alerts from "../../../alerts/static/reducer";
import markets from "../../../markets/static/reducer";
import constraints from "../../../constraints/static/reducer";
import costRevenue from "../../../net_revenue/static/reducer";
import userSettings from "../../../user_settings/static/reducer";
import notifications from "../../../notifications/static/reducer";
import residentialSD from "../../../residential_sd/static/reducer";
import { storage, capacity, formState } from "../../../power_dispatch/static/reducer";

const appReducer = combineReducers({
    auth,
    alerts,
    markets,
    constraints,
    costRevenue,
    notifications,
    storage,
    capacity,
    formState,
    userSettings,
    residentialSD,
    drawerNavigationMenu,
});

// Reset to initial state when logging out.
const baseReducer = (state, action) => {
    if (action.type === "USER_LOGGED_OUT") {
        state = undefined;
        localStorage.clear();
    }
    return appReducer(state, action);
};

export default baseReducer;
