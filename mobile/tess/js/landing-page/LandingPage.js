/**
 * SLAC 2019
 *
 * Created by: Jonathan G.
 *
 * Application landing page 
 */

import React from 'react'
import { connect } from 'react-redux'
import { View, Text, StyleSheet } from 'react-native'
import Button from '../common/components/TessButton'

/**
 * Landing page component
 */
class LandingPage extends React.Component {
    navigateToLogin = () => {
        this.props.navigation.navigate('LoginPage')
    }

    navigateToDisclaimer = () => {
        this.props.navigation.navigate('DisclaimerPage')
    }

    render() {
        return (
            <View>
                <View>
                    <Text>TESS logo placeholder</Text>
                </View>

                <View>
                    <Text>
                        Share your energy data, advance science, and take part in the value created.
                    </Text>
                    <Text>
                        TESS is secure, private, and free.
                    </Text>
                </View>

                <View>
                    <Button 
                        title='Join the movement'
                        accessibilityLabel='join the movement'
                        onPress={this.navigateToDisclaimer} />
                </View>

                <View>
                    <Text onPress={this.navigateToLogin}>
                        Already a member? <Text style={styles.loginLink}>Login</Text>
                    </Text>
                </View>
            </View>            
        )
    }
}

export default connect()(LandingPage)

const styles = StyleSheet.create({    
    loginLink: {
        fontSize: 12,
        color: 'blue',
        textDecorationLine: 'underline',
        textDecorationStyle: 'solid',
    }
})
