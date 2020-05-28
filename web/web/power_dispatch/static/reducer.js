const initialStorageState = {}

export function storage(state = initialStorageState, action) {
    switch (action.type) {        
        default:
            return state;
    }
}

const initialCapacityState = {
    systemLoadData: [],
    resourcesData: []
}

export function capacity(state = initialCapacityState, action) {
    switch (action.type) {        
        case 'SYSTEM_LOAD_DATA_UPDATED':
            return { ...state, systemLoadData: action.data };
        
        case 'RESOURCES_DATA_UPDATED':
            return { ...state, resourcesData: action.data };

        default:
            return state;
    }
}