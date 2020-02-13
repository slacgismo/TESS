/**
 * SLAC 2019
 * 
 * Created by: jongon
 * 
 * Modal wrapper for the login responses when user attempts to login/sign up
 */

'use strict'

import React from 'react'
import Button from '../TessButton'
import { connect } from 'react-redux'
import { hideModal } from '../../actions'
import { StyleSheet, View, Text } from 'react-native'

/**
 * Modal login component
 */
class ModalLogin extends React.PureComponent {
    render() {   
        return (
            <View>
                <View style={styles.modalContent}>
                    <Text style={styles.modalText}>{this.props.modalMessage}</Text>                    
                </View>
                <Button onPress={() => this.props.dispatch(hideModal())} borderRadius={0} title="OK" accessibilityLabel="Close sign in failed modal button"/>
            </View>            
        )
    }
}

export default connect()(ModalLogin)

const styles = StyleSheet.create({ 
    modalContent: {
        backgroundColor: 'white',
        padding: 22,
        justifyContent: 'center',
        alignItems: 'center',
        borderRadius: 0,
        borderColor: 'rgba(0, 0, 0, 0.1)',
    },
    modalText: {
        fontSize: 16,
        marginBottom: 10
    }
})