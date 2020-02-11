/**
 * SLAC 2017
 *
 * Created by: jongon
 *
 * Setup the whole application navigation. 
 */

import { createAppContainer } from 'react-navigation'
import { createStackNavigator } from 'react-navigation-stack'
import LandingPage from '../../landing-page/LandingPage'
import DisclaimerPage from '../../disclaimer-page/DisclaimerPage'

const appNavigator = createStackNavigator({
    LandingPage: {
        screen: LandingPage,
    },
    DisclaimerPage: {
        screen: DisclaimerPage
    }
}, { initialRouteName: 'LandingPage' })

const RootNavigatorWrapper = createAppContainer(appNavigator)
export default RootNavigatorWrapper
