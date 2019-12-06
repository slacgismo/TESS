/**
 * SLAC 2019
 *
 * Created by: Jonathan G.
 *
 * Create the redux store and persistor with the applied middlewares
 */

import thunk from 'redux-thunk'
import { createLogger } from 'redux-logger'
import { persistStore } from 'redux-persist'
import { applyMiddleware, createStore } from 'redux'
import { persistReducer } from './configure-reducers'


// logging middleware setup to be applied to the store
let isDebuggingInChrome = __DEV__ && window.navigator && !!window.navigator.userAgent
let logger = createLogger({
    predicate: (getState, action) => isDebuggingInChrome,
    collapsed: true,
    duration: true,
})

/**
 * Configure the Redux data store from the root reducer and hydrate it, if
 * needed, through the Persist framework
 */
function configureStore(encryptionKey) {
    // setup our redux data store with the attached middleware and the given reducer
    let _persistReducer = persistReducer.init(encryptionKey)
    const rootReducer = (state, action) => {
        if (action.type === 'CLEAR_ENTIRE_STATE') {
            // This resets the entire state back to the default except for the '_persist' key
            // which is used by persist-redux. Clearing this causes the persist to auto-rehydrate
            // with old data if you try purging, along with other unwanted side effects.
            const { _persist } = state
            state = { _persist }
        }
        return _persistReducer(state, action)
    }
    let store = applyMiddleware(thunk, logger)(createStore)(rootReducer)
    let persistor = persistStore(store)

    // Uncomment this purge to reset the state, useful if state gets out of whack when developing
    // or testing out cache functionality, etc.
    // persistor.purge();

    return { persistor, store }
}

export default configureStore