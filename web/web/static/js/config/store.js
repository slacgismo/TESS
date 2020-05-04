import thunk from "redux-thunk";
import { createLogger } from "redux-logger";
import baseReducer from "./base_reducer";
import storage from 'redux-persist/lib/storage';
import { persistStore, persistReducer } from 'redux-persist';
import { createStore, applyMiddleware, compose } from "redux";

// Logger must be last middleware in chain, otherwise it will log thunk 
// and promise, not actual actions (https://github.com/theaqua/redux-logger/issues/20).
let enhancer = null;
let middleware = [thunk];
const persistConfig = {
    key: 'root',
    storage,
};
const persistedReducer = persistReducer(persistConfig, baseReducer);

// Enabling browser redux extension (https://github.com/zalmoxisus/redux-devtools-extension)
const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

// we'll remove the logger from production in the future
middleware.push(createLogger());
enhancer = composeEnhancers(
    applyMiddleware(...middleware)
);

let store = createStore(persistedReducer, enhancer);
let persistor = persistStore(store);

export default function configureStore() {
    return { store, persistor };
}
