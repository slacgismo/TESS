const initialStorageState = {
    systemLoadData: [],
    resourcesData: [],
    formData: {}
}

export function storage(state = initialStorageState, action) {
    switch (action.type) {
        case 'STORAGE_SYSTEM_LOAD_DATA_UPDATED':
            return { ...state, systemLoadData: action.data };

        case 'STORAGE_RESOURCES_DATA_UPDATED':
            return { ...state, resourcesData: action.data };

        default:
            return state;
    }
}

const initialCapacityState = {
    systemLoadData: [],
    resourcesData: [],
    transformerData: {},
    formData: {},
    alertSettings: {}
}

export function capacity(state = initialCapacityState, action) {
    switch (action.type) {
        case 'CAPACITY_SYSTEM_LOAD_DATA_UPDATED':
            return { ...state, systemLoadData: action.data };

        case 'CAPACITY_RESOURCES_DATA_UPDATED':
            return { ...state, resourcesData: action.data };

        default:
            return state;
    }
}

export function formState(state = initialCapacityState, action) {
    switch (action.type) {
        case 'SAVE_FORM_DATA':
            return { ...state, formData: action.data };
        default:
            return state;
    }
}

export function transformerDataState(state = initialCapacityState, action) {
    switch (action.type) {
        case 'TRANSFORMER_DATA_UPDATED':
            return { ...state, transformerData: action.data };
        default:
            return state;
    }
}

export function alertSettingsState(state = initialCapacityState, action) {
    switch (action.type) {
        case 'ALERT_SETTINGS_UPDATED':
            return { ...state, alertSettings: action.data };
        default:
            return state;
    }
}
