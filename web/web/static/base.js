import React from 'react';
import { Provider } from 'react-redux';
import TopBar from './components/top_bar';
import configureStore from './config/store';
import NavigationDrawer from './components/navigation_drawer';
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
                    <TopBar isVisible={this.props.isVisible}/>
                    <NavigationDrawer isVisible={this.props.isVisible}/>
                    {this.props.children}
                </PersistGate>
            </Provider>
        );
    }
}

export default ConnectedComponentWrapper;