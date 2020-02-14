/**
 * SLAC 2019
 *
 * Created by: Jonathan G.
 *
 * Component that handles the sign up and the sign in flow
 */

import React from 'react'
import { connect } from 'react-redux'
import { showModal } from '../common/actions'
import Button from '../common/components/TessButton'
import { View, Text, StyleSheet, TextInput, Platform } from 'react-native'

/**
 * Sign In/Sign Up page component
 */
class SignInSignUpPage extends React.Component {
    constructor() {
        super()

        this.state = {
            email: '',
            password: ''
        }
    }

    navigateToPhoneVerification = () => {
        this.props.navigation.navigate('PhoneVerificationPage')
    }

    navigateToMyWallet = () => {
        this.props.navigation.navigate('')
    }

    submit = () => {
        const isUsernamePasswordValid = this.validateUsernamePassword()
        if (!isUsernamePasswordValid) {
            this.props.dispatch(showModal('LOGIN', {
                modalMessage: 'Email and Password are required fields, please do not leave them blank.'
            }))
        } else {
            const { navigation } = this.props
            const isSignUp = navigation.getParam('isSignUp', false)
            if(isSignUp) {
                // TODO: navigate the user to the appropriate phone verification page
                // after actually creating their account
                this.navigateToPhoneVerification()
            } else {
                // TODO: actually send params to the backend and authenticate the user...
                // then navigate them to where they need to go
                this.navigateToMyWallet()
            }            
        }
    }

    validateUsernamePassword = () => {
        // make sure the input isn't blank
        const email = this.state.email.trim(),
              password = this.state.password.trim()

        return email && password
    }

    handleEmailTextChange = (v) => {
        this.setState({email: v})
    }

    handlePasswordTextChange = (v) => {
        this.setState({password: v})
    }

    render() {
        const { navigation } = this.props
        const isSignUp = navigation.getParam('isSignUp', false)
        return (
            <View>
                <View style={styles.logoContainer}>
                    <Text>TESS logo placeholder</Text>
                </View>

                <View style={styles.tessDescriptionContainer}>
                    <Text style={styles.titleText}>
                        Sign {isSignUp ? 'Up' : 'In'} with Holy Cross
                    </Text>
                    
                    <View style={styles.spacer}/>
                    
                    <TextInput 
                        placeholder='Username'
                        onChangeText={this.handleEmailTextChange}
                        autoCapitalize='none'
                        keyboardType='email-address'
                        autoCorrect={false}
                        autoFocus={true}
                        returnKeyType={'next'}
                        accessible={true}
                        accessibilityLabel="Email/Username Input Field"
                        onSubmitEditing={this.submit}
                        blurOnSubmit={false}
                        placeholderTextColor='black'/>

                    <TextInput
                        placeholder='Password'
                        secureTextEntry={true}
                        returnKeyType={'done'}
                        accessibilityLabel="Password Input Field"
                        onChangeText={this.handlePasswordTextChange}
                        placeholderTextColor='black'
                        onSubmitEditing={this.submit}/>
                </View>

                <View style={styles.button}>
                    <Button 
                        title={isSignUp ? 'Sign Up' : 'Login'}
                        accessibilityLabel='sign up/login button'
                        onPress={this.submit} />
                </View>
            </View>            
        )
    }
}

export default connect()(SignInSignUpPage)

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
