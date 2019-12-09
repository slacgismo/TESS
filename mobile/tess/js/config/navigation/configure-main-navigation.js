/**
 * SLAC 2017
 *
 * Created by: jongon
 *
 * Setup the whole application navigation. 
 */

import React from 'react'
import { connect } from 'react-redux'
import { createAppContainer } from 'react-navigation'
import { LandingPage } from '../../landing-page/LandingPage'
import { createStackNavigator } from 'react-navigation-stack'

const appNavigator = createStackNavigator({
    Home: {
        screen: LandingPage,
    },
})

const RootNavigatorWrapper = createAppContainer(appNavigator)
export default RootNavigatorWrapper
