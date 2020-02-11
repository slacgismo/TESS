/**
 * SLAC 2019
 *
 * Created by: Jonathan G.
 *
 * Disclaimer Page
 */

import React from 'react'
import { connect } from 'react-redux'
import { View, Text, StyleSheet } from 'react-native'
import Button from '../common/components/TessButton'

/**
 * Disclaimer page component
 */
class DisclaimerPage extends React.Component {    

    navigateToSignup = () => {
        this.props.navigation.navigate('SignupPage')
    }

    render() {
        return (
            <View>
                <View>
                    <Text>TESS logo placeholder</Text>
                </View>

                <View>
                    <Text>
                        Terms and Conditions
                    </Text>
                    <Text>
                        You agree to let Holy Cross Energy collect data about you, your house, 
                        and when you certain appliances. Holy Cross Energy only shares this data 
                        with organizations that are willing to pay you for it. You may deny any 
                        organization access to your data at any time.
                    </Text>
                    <Text>
                        You agree to let Holy Cross Energy control your appliances based on your preferences.
                        You agree to be compensated for control actions through bill credits. You may opt out
                        of control temporarily any time.
                    </Text>
                </View>

                <View>
                    <Button 
                        title='I Agree'
                        accessibilityLabel='agree to terms and conditions'
                        onPress={this.navigateToSignup} />
                </View>
            </View>            
        )
    }
}

export default connect()(DisclaimerPage)

const styles = StyleSheet.create({    
    loginLink: {
        fontSize: 12,
        color: 'blue',
        textDecorationLine: 'underline',
        textDecorationStyle: 'solid',
    }
})
