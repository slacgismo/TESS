import ky from 'ky';

/**
 * Define the network API abstraction layer
 */
export const api = {
    network: ky,
    authToken: null,    
    url: '/api/v1/',

    /** Pseudo-private call to retrieve the Auth Token from our storage */
    getAuthToken: () => { return this.authToken },

    /** Set the tess Auth token by saving it into our storage */
    setAuthToken: (token) => { 
        this.authToken = token
        this.network.extend({
            hooks: {
                beforeRequest: [
                    request => {
                        request.headers.set('Authorization', `Token ${this.getAuthToken()}`);
                    }
                ]
            }
        })
    },
    
    get: async (resource, successHandler, errorHandler) => {
        try {
            const response = await api.network.get(`${api.url}${resource}`).json();
            if(successHandler && typeof successHandler == "function") {
                successHandler(response)
            }
        } catch(e) {            
            if(e instanceof ky.HTTPError) {
                console.warn("there was an HTTPError");
                if(errorHandler && typeof errorHandler == "function") {
                    errorHandler(e.response)
                }
            } else {
                throw e;
                // will call global handler
            }
            
        }
    }   
}
