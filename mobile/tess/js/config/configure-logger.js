/**
 * SLAC 2019
 *
 * Created by: Jonathan G.
 *
 * Initialize the TESS monitoring systems.
 */

import { version } from '../../package'
import { NativeModules } from 'react-native'
import { environments as envVars } from './env-params'
import { default_environment as environment } from './env'

// TODO: Create the native logger module
//const logger = NativeModules.TessLogger

export default function initializeMonitoringSystems() {
    // debug log messages are never sent to papertrail and should be removed after dev.
    global.LOG = (...args) => {
        console.log('||------------------------------------------------------------||')
        console.log(...args)
        console.log('||------------------------------------------------------------||')
        return args[args.length - 1]
    }

    // these are log messages we need to be aware of, so they are aggregated in papertrail
    global.INFO = (message, ...args) => { rxLog('INFO', message, ...args) }
    global.NETW = (message, ...args) => { rxLog('NETW', message, ...args) }
    global.WARN = (message, ...args) => { rxLog('WARN', message, ...args) }
    global.ERRO = (message, ...args) => { rxLog('ERRO', message, ...args) }

    function rxLog(logLevel, message, ...args) {
        if(environment === 'dev' || environment === 'debug') {
            global.LOG(message, ...args)
        }

        // const logArgs = args.length > 0 ? ` ${JSON.stringify(...args)}` : ''

        // logger.wine(environment.toUpperCase(),
        //             logLevel,
        //             `${message}${logArgs}`,        
        //             global.userId ? global.userId.toString(): 'anon',
        //             `${version}${__DEV__ ? ' - DEBUG': ''}`)
    }
}

