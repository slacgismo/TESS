import thunk from "redux-thunk";
import { createLogger } from "redux-logger";
import baseReducer from "../reducers/common";
import { createStore, applyMiddleware, compose } from "redux";

// Logger must be last middleware in chain, otherwise it will log thunk and promise, not actual actions (https://github.com/theaqua/redux-logger/issues/20).
let enhancer = null;
let middleware = [thunk];

// Enabling browser redux extension (https://github.com/zalmoxisus/redux-devtools-extension)
const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

// we'll remove the logger from production in the future
middleware.push(createLogger());
enhancer = composeEnhancers(applyMiddleware(...middleware));

export default function configureStore() {
    return createStore(baseReducer, enhancer);
}
