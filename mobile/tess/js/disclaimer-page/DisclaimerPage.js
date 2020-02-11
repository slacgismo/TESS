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
                <View style={styles.logoContainer}>
                    <Text>TESS logo placeholder</Text>
                </View>

                <View style={styles.tessDescriptionContainer}>
                    <Text style={styles.titleText}>
                        Terms and Conditions
                    </Text>
                    <View style={styles.spacer}/>
                    <Text style={styles.tessDescriptionText}>
                        You agree to let Holy Cross Energy collect data about you, your house, 
                        and when you certain appliances. Holy Cross Energy only shares this data 
                        with organizations that are willing to pay you for it. You may deny any 
                        organization access to your data at any time.
                    </Text>
                    <View style={styles.spacer}/>
                    <Text style={styles.tessDescriptionText}>
                        You agree to let Holy Cross Energy control your appliances based on your preferences.
                        You agree to be compensated for control actions through bill credits. You may opt out
                        of control temporarily any time.
                    </Text>
                </View>

                <View style={styles.button}>
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
