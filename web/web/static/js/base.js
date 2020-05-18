import React from 'react';
import { Button } from '@rmwc/button';
import { Provider } from 'react-redux';
import TopBar from './components/top_bar';
import configureStore from './config/store';
import { SnackbarQueue } from '@rmwc/snackbar';
import { Typography } from '@rmwc/typography';
import  { queue } from './components/app_notification_queue';
import NavigationDrawer from './components/navigation_drawer';
import { PersistGate } from 'redux-persist/integration/react';

import '@rmwc/button/styles';
import '@rmwc/snackbar/styles';
import '@rmwc/typography/styles';

const { store, persistor } = configureStore();

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
                    <div className={`load-price-notification-container ${!this.props.isVisible ? "lpn-hidden" : ""}`}>
                        <div className="lpn-pull-left">
                            {/* <Typography use="headline5">{this.props.pageTitle || ""}</Typography> */}
                        </div>
                        <div className="lpn-pull-right">
                            <Button label="LOAD" trailingIcon={
                                <div
                                    style={{
                                        background: 'green',
                                        width: '16px',
                                        height: '16px',
                                        borderRadius: '100px'
                                    }}
                                />
                            } />
                            <div className='lpn-spacer'></div>
                            <Button label="PRICE" trailingIcon={
                                <div
                                    style={{
                                        background: 'red',
                                        width: '16px',
                                        height: '16px',
                                        borderRadius: '100px'
                                    }}
                                />
                            } />
                        </div>
                    </div>
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