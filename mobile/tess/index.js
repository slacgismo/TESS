/**
 * SLAC 2019
 *
 * Created by: Jonathan G.
 *
 * Main application entry point
 */

import { Root } from './js/app'
import { AppRegistry } from 'react-native'
import { name as appName } from './app.json'
import initializeMonitoringSystems from './js/config/configure-logger'

initializeMonitoringSystems()
AppRegistry.registerComponent(appName, () => Root)
