import React from 'react';
import { Provider } from 'react-redux';
import configureStore from './config/store';

class ConnectedComponentWrapper extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <Provider store={configureStore()}>
                {this.props.children}
            </Provider>
        );
    }
}

export default ConnectedComponentWrapper;