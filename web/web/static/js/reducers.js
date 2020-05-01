const initialState = {
    isDrawerOpen: true,
    selectedMenuName: "power-dispatch"
}

export default function drawerNavigationMenu(state = initialState, action) {
    switch (action.type) {        
        case "TOGGLE_NAVIGATION_DRAWER":
            return { ...state, isDrawerOpen: !state.isDrawerOpen }

        case "SELECT_MENU_OPTION":
                return { ...state, selectedMenuName: action.selectedMenuName }
        
        default:
            return state
    }
}
