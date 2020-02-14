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
import CodeVerificationPage from '../../phone-verification-pages/CodeVerificationPage'
import PhoneVerificationPage from '../../phone-verification-pages/PhoneVerificationPage'

const appNavigator = createStackNavigator({
    LandingPage: {
        screen: LandingPage,
    },
    DisclaimerPage: {
        screen: DisclaimerPage
    },
    SignInSignUpPage: {
        screen: SignInSignUpPage
    },
    PhoneVerificationPage: {
        screen: PhoneVerificationPage
    },
    CodeVerificationPage: {
        screen: CodeVerificationPage
    }
}, { initialRouteName: 'LandingPage' })

const RootNavigatorWrapper = createAppContainer(appNavigator)
export default RootNavigatorWrapper
