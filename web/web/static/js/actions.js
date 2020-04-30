export function toggleNavigationDrawer() {
    return {
        type: "TOGGLE_NAVIGATION_DRAWER"
    }
}

export function selectMenuOption(selectedMenuName) {
    return {
        type: "SELECT_MENU_OPTION",
        selectedMenuName
    }
}