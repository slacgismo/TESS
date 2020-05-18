import React from 'react';
import { Provider } from 'react-redux';
import TopBar from './components/top_bar';
import configureStore from './config/store';
import { SnackbarQueue } from '@rmwc/snackbar'; 
import  { queue } from './components/app_notification_queue';
import NavigationDrawer from './components/navigation_drawer';
import { PersistGate } from 'redux-persist/integration/react';

import '@rmwc/snackbar/styles';

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
                    <SnackbarQueue
                        messages={queue.messages}
                        leading
                        stacked
                    />
                    {this.props.children}
                </PersistGate>
            </Provider>
        );
    }
}

export default ConnectedComponentWrapper;