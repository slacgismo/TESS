const initialState = {
    isDrawerOpen: true,
    selectedMenuName: "power-dispatch",
    userLoggedOut: false,
};

export default function drawerNavigationMenu(state = initialState, action) {
    switch (action.type) {
        case "TOGGLE_NAVIGATION_DRAWER":
            return { ...state, isDrawerOpen: !state.isDrawerOpen };

        case "SELECT_MENU_OPTION":
            return { ...state, selectedMenuName: action.selectedMenuName };

        case "USER_LOGGED_OUT":
        case "RESET_USER_LOGGED_OUT":
            return { ...state, userLoggedOut: action.userLoggedOut };

        default:
            return state;
    }
}
