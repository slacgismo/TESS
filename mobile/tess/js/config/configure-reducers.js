/**
 * SLAC 2019
 *
 * Created by: Jonathan G.
 *
 * Setup the reducer persistor and combine all the declared reducers;
 * redux-persist configuration is also determined here. Lastly, we
 * pass in react native's AsyncStorage option to redux-persist. In the future we may
 * swap out AsyncStorage for a more robust solution.
 *
 * AsyncStorage thoughts from FB: https://facebook.github.io/react-native/docs/asyncstorage.html
 *
 * PLEASE do not add actual reducers here!
 */

import { modal } from '../common/reducers'
import { persistCombineReducers } from 'redux-persist'
import createEncryptor from 'redux-persist-transform-encrypt'
import AsyncStorage from '@react-native-community/async-storage'

// build the reducer tree to be combined
const reducerSpec = {
    modal
}

// redux-persistify
export const persistReducer = {
    init: (encryptionKey) => {
        const encryptor = createEncryptor({
            secretKey: encryptionKey,
            onError: function (error) {
                global.ERRO("There was an error with the encryption transform applied to redux-persist; e = ", error)
            }
        })

        const persistConfig = {
            key: 'root',
            storage: AsyncStorage,
            transforms: [encryptor]
        }
        return persistCombineReducers(persistConfig, reducerSpec)
    }
}
