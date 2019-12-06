/**
 * SLAC 2019
 *
 * Created by: Jonathan G.
 *
 * Load the TESS Root application container
 */


import React from 'react'
import cryptojs from 'crypto-js'
import { Provider } from 'react-redux'
import { hideModal } from './common/actions'
import * as Keychain from 'react-native-keychain'
import { environments } from './config/env-params'
import { default_environment } from './config/env'
import configureStore from './config/configure-store'
import TessModal from './common/components/TessModal'
import { StatusBar, Platform, Text, TextInput } from 'react-native'
import { PersistGate } from 'redux-persist/es/integration/react'
import RootNavigatorWrapper from './config/navigation/configure-main-navigation'

export let globalStore = null
export let globalPersistor = null
export let navRef = null

/**
 * Root component wrapper for the whole tess app. The child component here
 * is actually the Navigation component which establishes a Navigator for
 * the app.
 */
export class App extends React.Component {
    constructor(props) {
        super(props)
        // currently it's a bit difficult the prevent horrible scability due to large
        // font sizes bc of OS accessibility settings
        Text.defaultProps = Text.defaultProps || {}
        Text.defaultProps.allowFontScaling = false
        TextInput.defaultProps = TextInput.defaultProps || {}
        TextInput.defaultProps.allowFontScaling = false

        this.onLanguagesChange = this.onLanguagesChange.bind(this)
        this.getCurrentRouteName = this.getCurrentRouteName.bind(this)
        this.state = {
            encryptionKey: null
        }
    }

    /** Log each nav state change so we can more easily re-create a user's steps through the app */
    onNavigationStateChange(prevState, currentState) {
        const currentScreen = this.getCurrentRouteName(currentState);
        const prevScreen = this.getCurrentRouteName(prevState);
        if(prevScreen !== currentScreen) {
            global.INFO(`Changing screens from: ${prevScreen} - to: ${currentScreen}`)
        }
    }

    /** Retrieve the route name so we can properly log navigation when its state changes */
    getCurrentRouteName(navigationState) {
        if (!navigationState) {
            return null
        }

        const route = navigationState.routes[navigationState.index];

        // dive into nested navigators
        if (route.routes) {
            return this.getCurrentRouteName(route);
        }
        return route.routeName;
    }    

    /**
     * Determine whether an encryption key exists when the app loads
     */
    componentDidMount() {
        this.verifyEncryptionSetup()
    }

    /**
     * Function that asynchronously tries to access the keychain/keystore for an
     * encryption key. If one doesn't exist, we generate one via a random cryptojs hash
     * and then save it to the keychain/keystore.
     */
    async verifyEncryptionSetup() {
        const user = 'TESS_APPLICATION_USER';
        let encryptionKey;

        try {
            encryptionKey = await Keychain.getGenericPassword();
            if(!encryptionKey) {
                encryptionKey = cryptojs.enc.Hex.stringify(cryptojs.lib.WordArray.random(64))
                this.setState({encryptionKey: encryptionKey})
                await Keychain.setGenericPassword(user, encryptionKey)
            } else {
                // what is returned from the keychain is a bit abstracted in a keystore obj...
                this.setState({encryptionKey: encryptionKey.password})
            }
        } catch (error) {            
            global.ERRO('There was an error accessing the keychain; e = ', error)
            this.setState({encryptionKey: 'unsafe-encryption-key'})
        }
    }

    render() {
        if(this.state.encryptionKey === null) {
            // no valid encryption key is set yet
            return null
        }
        const { persistor, store } = configureStore(this.state.encryptionKey)
        globalStore = store
        globalPersistor = persistor

        return (
            <Provider store={store}>
                <PersistGate persistor={globalPersistor} onBeforeLift={() => store.dispatch(hideModal())}>
                    <View style={{ flex: 1, flexDirection: 'column' }}>
                        <RootNavigatorWrapper
                            ref={nav => {navRef = nav}}
                            onNavigationStateChange={(prevState, currentState) =>
                                this.onNavigationStateChange(prevState, currentState)} />
                        <OfflineNotice />
                        <TessModal />
                    </View>
                </PersistGate>
            </Provider>
        )
    }
}
