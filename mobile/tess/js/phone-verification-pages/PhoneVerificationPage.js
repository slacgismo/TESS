/**
 * SLAC 2019
 *
 * Created by: Jonathan G.
 *
 * Component that handles the phone verification flow
 */

import React from 'react'
import { connect } from 'react-redux'
import { showModal } from '../common/actions'
import Button from '../common/components/TessButton'
import { View, Text, StyleSheet, TextInput, Platform } from 'react-native'

/**
 * Phone Verification page component
 */
class PhoneVerificationPage extends React.Component {
    constructor() {
        super()

        this.state = {
            phoneNumber: ''
        }
    }

    navigateToCodeVerification = () => {
        this.props.navigation.navigate('CodeVerificationPage')
    }
    
    submit = () => {
        const isPhoneNumberValid = this.validatePhoneNumber()
        if (!isPhoneNumberValid) {
            // this.props.dispatch(showModal('LOGIN', {
            //     modalMessage: 'Email and Password are required fields, please do not leave them blank.'
            // }))
        } else {
                        
        }
    }

    validatePhoneNumber = () => {
        // make sure the input isn't blank
        const phoneNumber = this.state.phoneNumber.trim()
        return phoneNumber.length > 0        
    }

    handlePhoneNumberChange = (v) => {
        this.setState({phoneNumber: v})
    }

    render() {        
        return (
            <View>
                <View style={styles.logoContainer}>
                    <Text>TESS logo placeholder</Text>
                </View>

                <View style={styles.tessDescriptionContainer}>
                    <Text style={styles.titleText}>
                        Verify your device
                    </Text>
                    
                    <View style={styles.spacer}/>
                    
                    <TextInput 
                        placeholder='Phone Number'
                        onChangeText={this.handlePhoneNumberChange}
                        keyboardType='phone-pad'
                        autoFocus={true}
                        returnKeyType={'done'}
                        accessible={true}
                        accessibilityLabel="Phone number input field"
                        onSubmitEditing={this.submit}
                        blurOnSubmit={false}
                        placeholderTextColor='black'/>
                </View>

                <View style={styles.button}>
                    <Button 
                        title='Send Verification Code'
                        accessibilityLabel='send verification code button'
                        onPress={this.submit} />
                </View>
            </View>            
        )
    }
}

export default connect()(PhoneVerificationPage)

const styles = StyleSheet.create({ 
    logoContainer: {
        alignItems: 'center',
        marginHorizontal: 15,
        marginTop: 75,
        marginBottom: 45
    },
    titleText: {
        fontSize: 16,
        fontWeight: 'bold'
    },
    tessDescriptionContainer: {
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingVertical: 25,
        marginBottom: 45,
        borderColor: 'black',
        borderWidth: 2
    },
    tessDescriptionText: {
        textAlign: 'center',
        fontSize: 14
    },
    spacer: {
        marginTop: 30
    },
    button: {
        marginHorizontal: 20
    }
})
