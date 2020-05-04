import ky from 'ky';

/**
 * Define the network API abstraction layer
 */
export const api = {
    _api: ky.extend({
        hooks: {
            beforeRequest: [
                request => {
                    request.headers.set('Authorization', `Token ${api.getAuthToken()}`);
                }
            ]
        }
    }),
    authToken: null,
    url: '/api/v1/',

    /** Pseudo-private call to retrieve the Auth Token from our storage */
    getAuthToken: () => { return this.authToken },

    /** Set the tess Auth token by saving it into our storage */
    setAuthToken: (token) => { this.authToken = token },
    
    get: async (resource) => {
        return await _api.get(`${url}${resource}`).json()
    }   
}
