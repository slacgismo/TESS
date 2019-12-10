/**
 * SLAC 2019
 *
 * Created by: Jonathan G.
 *
 * Application splash page - doesn't do much
 */

import React from 'react'
import { connect } from 'react-redux'
import { View, Text } from 'react-native'

/**
 * Landing page component
 */
class LandingPage extends React.Component {
    render() {
        return (
            <View>
                <Text>Just a random landing page for TESS</Text>
            </View>
        )
    }
}

export default connect()(LandingPage)
