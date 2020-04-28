import React from 'react';
import { Provider } from 'react-redux';
import configureStore from './config/store';
import { PersistGate } from 'redux-persist/integration/react';

const { store, persistor } = configureStore()

class ConnectedComponentWrapper extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <Provider store={store}>
                <PersistGate persistor={persistor}>
                    {this.props.children}
                </PersistGate>
            </Provider>
        );
    }
}

export default ConnectedComponentWrapper;