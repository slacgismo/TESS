import ky from 'ky';

/**
 * Define the network API abstraction layer
 */
export const api = {
    network: ky,    
    url: '/api/v1/',
    
    post: async (resource, data, successHandler, errorHandler) => {
        try {
            const response = await api.network.post(`${api.url}${resource}`, data).json();
            if(successHandler && typeof successHandler === "function") {
                successHandler(response);
            }            
        } catch(e) {
            api.handleApiError(e, errorHandler);
        }
    },

    get: async (resource, successHandler, errorHandler) => {
        try {
            const response = await api.network.get(`${api.url}${resource}`).json();
            if(successHandler && typeof successHandler === "function") {
                successHandler(response);
            }
        } catch(e) {            
            api.handleApiError(e, errorHandler);
        }
    },
    
    handleApiError: (exception, errorHandler) => {
        if(exception instanceof ky.HTTPError) {
            console.warn("there was an HTTPError");
            if(errorHandler && typeof errorHandler === "function") {
                errorHandler(exception.response);
            }
        } else {
            throw exception;
            //TODO: write a global/api error handler
        }
    }
}
