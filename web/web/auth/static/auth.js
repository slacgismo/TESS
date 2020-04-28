import React from 'react';
import ReactDOM from 'react-dom';

class Auth extends React.Component {
    render() {
        return (
            <h1>HELLO AUTH PAGE</h1>
        );
    }
}

ReactDOM.render(<Auth />, document.getElementById('master-container'));