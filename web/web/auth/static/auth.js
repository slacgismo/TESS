import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import '@material/button/dist/mdc.button.css';
import ConnectedComponentWrapper from '../../static/base';

import * as action from './actions';

class Auth extends React.Component {
    onClick = () => {
        this.props.dispatch(action.loginSuccessful('asdf'));
    }

    render() {
        return (
            <div>Auth Page</div>
        );
    }
}

const ConnectedAuth = connect(state => ({
    token: state.auth.token
  }))(Auth)

const authElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedAuth/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(authElement, document.getElementById('master-container'));