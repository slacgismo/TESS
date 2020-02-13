/**
 * SLAC 2017
 *
 * Created by: jongon
 *
 * Setup the whole application navigation. 
 */

import { createAppContainer } from 'react-navigation'
import LandingPage from '../../landing-page/LandingPage'
import { createStackNavigator } from 'react-navigation-stack'
import DisclaimerPage from '../../disclaimer-page/DisclaimerPage'
import SignInSignUpPage from '../../sign-in-sign-up-page/SignInSignUpPage'

const appNavigator = createStackNavigator({
    LandingPage: {
        screen: LandingPage,
    },
    DisclaimerPage: {
        screen: DisclaimerPage
    },
    SignInSignUpPage: {
        screen: SignInSignUpPage
    }
}, { initialRouteName: 'LandingPage' })

const RootNavigatorWrapper = createAppContainer(appNavigator)
export default RootNavigatorWrapper
