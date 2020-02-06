/**
 * SLAC 2020
 *
 * Created by: jongon
 *
 * Network abstraction layer
 */

import { globalStore } from '../app'
import { signout, showModal } from './actions'
import { environments } from '../config/env-params'
import { default_environment } from '../config/env'
import { version as applicationVersion } from '../../package'
const v4 = require('uuid/v4')

// define the methods we currently accept
const METHOD = {
    GET: 'GET',
    HEAD: 'HEAD',
    PUT: 'PUT',
    DELETE: 'DELETE',
    PATCH: 'PATCH',
    POST: 'POST'
}

/**
 * Define the network API abstraction layer
 */
export const api = {
    authToken: null,
    root: environments[default_environment].baseURL + '/api/',

    /** Pseudo-private call to retrieve the Auth Token from our storage */
    getAuthToken: () => { return this.authToken },

    /** Set the tess Auth token by saving it into our storage */
    setAuthToken: (token) => { this.authToken = token },
    
    /**
     * Pseudo-private fn that reconciles HTTP parameter dependencies, namely, headers
     * If using SSO, make authType = 'Bearer' and set the provider header
     */
    reconcileParameters: (additionalHeaders, requiresAuth, authType = 'Token') => {
        let authToken = null,
            params = {},
            type = authType,
            baseTypeHeaders = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Authority-Provider': 'native',
                'X-Application-Version': applicationVersion
            }

        if (!requiresAuth) {
            params.headers = { ...additionalHeaders, ...baseTypeHeaders }
        } else {
            authToken = api.getAuthToken()            
            params.headers = { 
                ...baseTypeHeaders, 
                'Authorization': `${type} ${authToken}`,
                ...additionalHeaders }
        }

        return params
    },

    /** Pseudo-private 'fetch' abstraction */
    call: async (apiVersion, resource, parameters) => {
        const url = `${api.root}v${apiVersion}/${resource}`
        api.logRequest(url, parameters)

        const response = await fetch(url, parameters)        
        return response
    },

    callExternal: async (url, parameters) => {
        api.logRequest(url, parameters)
        const response = await fetch(url, parameters)
        return response
    },

    getExternal: async (url, additionalHeaders = {}) => {
        const params = api.reconcileParameters({additionalHeaders}, false)
        params.method = METHOD.GET
        return await api.callExternal(url, params)
    },

    /** Perform a GET request on a given resource */
    get: async (resource, apiVersion = 1, additionalHeaders = {}, requiresAuth = true) => {
        let params = api.reconcileParameters(additionalHeaders, requiresAuth)
        params.method = METHOD.GET
        return await api.call(apiVersion, resource, params)
    },

    /** Perform a POST request to the given resource */
    post: async (resource, body, apiVersion = 1, additionalHeaders = {}, requiresAuth = true) => {
        let params = api.reconcileParameters(additionalHeaders, requiresAuth)
        params.method = METHOD.POST
        params.body = JSON.stringify(body)
        return await api.call(apiVersion, resource, params)
    },

    /** Perform a PATCH request to the given resource */
    patch: async (resource, body, apiVersion = 1, additionalHeaders = {}, requiresAuth = true) => {
        let params = api.reconcileParameters(additionalHeaders, requiresAuth)
        params.method = METHOD.PATCH
        params.body = JSON.stringify(body)
        return await api.call(apiVersion, resource, params)
    },

    /** Perform a PUT request to the given resource */
    put: async (resource, body, apiVersion = 1, additionalHeaders = {}, requiresAuth = true) => {
        let params = api.reconcileParameters(additionalHeaders, requiresAuth)
        params.method = METHOD.PUT

        if(body instanceof FormData) {
            params.body = body
        } else {
            params.body = JSON.stringify(body)
        }

        return await api.call(apiVersion, resource, params)
    },

    /** Perform a DELETE request to the given resource */
    delete: async (resource, apiVersion = 1, additionalHeaders = {}, requiresAuth = true) => {
        let params = api.reconcileParameters(additionalHeaders, requiresAuth)
        params.method = METHOD.DELETE
        return await api.call(apiVersion, resource, params)
    },
    
    /**
     * API level abstraction for handling response status codes     
     */
    handleResponseStatus: (response, signoutOnAccessForbidden = false) => {
        global.NETW(`RESOURCE: ${response.url} STATUS: ${response.status}`)
        if (!response.ok) {
            // if the user is already signed in but is now getting an un-auth'ed, send them back to the landing page
            // otherwise the user may be getting a valid response from the auth_token endpoint and the view will handle
            if(response.status === 401 && !signoutOnAccessForbidden && this.authToken) {
                globalStore.dispatch(signout())
            }

            // parsing an error can lead to SyntaxError depending on which error is being returned e.g. 504
            const parsedResponsePromise = response.json().then((err) => {
                // the error was parseable, i.e. valid JSON
                global.ERRO('There was an error performing your API request', err)
                let error = new Error(err.detail)
                error.response = response
                error.serverError = err
                if("compatible" in err && err["compatible"] === false) {
                    globalStore.dispatch(showModal('FORCE_UPGRADE', { detail: err.detail }))
                }
                throw error
            }).catch((err) => {
                if (err.name !== 'SyntaxError') {
                    // this was a parseable error, so just re-throw so the caller may handle the
                    // json error response appropriately.
                    throw err
                }
                global.ERRO(`There was an issue processing the request and parsing the response. HTTP status code ${response.status}`)
                // we could not parse the error response, return a generic error
                let error = new Error('There was an issue processing your request. Please try again. The TESS team has been notified.')
                error.response = response
                throw error
            })
            return parsedResponsePromise
        }

        if(response.status === 204) {
            // there's no content to parse, so it would throw an error, this is common during delete ops
            return response
        }

        return response.json()
    },
    
    /**
     * Internal logging routine for the api object - primary purpose is to redact sensitive information
     */
    logRequest: (url, params) => {
        // make sure we redact the auth token and, if present, the password
        let strippedParams = Object.assign({}, params, { headers: { 'Authorization': '--redacted--' } })

        if(params.body) {
            const parsedBody = params.body instanceof FormData
                ? params.body
                : JSON.parse(params.body)

            // redact the password for security
            if(parsedBody.password) {
                parsedBody.password = '--redacted--'
            }

            // redact base64 encoded images due to size constraints - instead of recursively
            // trying to find these, get around it by doing a string search
            let stringifiedBody = JSON.stringify(parsedBody)
            const startOfImageIndex = stringifiedBody.indexOf('data:image/')
            if(~startOfImageIndex) {
                // get the index of where the image ends - basically where the next obj key begins
                const endOfImageIndex = stringifiedBody.indexOf('","', startOfImageIndex)
                const b64Image = stringifiedBody.substring(startOfImageIndex, endOfImageIndex)
                // replace the base64 string
                stringifiedBody = stringifiedBody.split(b64Image).join('--base64 image redacted--')
                // finally, assign the new value back to the body of the request - parsedBody is ReadOnly
                newRequestBody = JSON.parse(stringifiedBody)
                strippedParams = Object.assign({}, strippedParams, { body: newRequestBody })
            } else {
                strippedParams = Object.assign({}, strippedParams, { body: parsedBody })
            }
        }

        global.NETW(`RESOURCE: ${url} PARAMETERS:`, strippedParams)
    }
}
