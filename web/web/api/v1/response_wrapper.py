from flask import jsonify

class ApiResponseWrapper(object):
    """
    A super simple API response wrapper.
    This should allow us to standardize all API responses.

    Currently, it is expected that if the errors array is not empty,
    then the results object is not populated. TODO: enforce or remove in code.

    The results object can grow to support pagination pretty easily.
    The results object has the following expectations:
     - detail [String]: an explanation of the response, if needed.
        Something like, entity successfully created, or objects successfully retrieved
     - count [integer]: represents the number of entities in the data array
     - data [array]: an array of objects - generally serialized models

    The errors object is currently an array. Which I'd expect to be mainly strings or 
    objects. Most cases len(errors) = 1. However in certain scenarios, say login, there
    can be two strings in the array, e.g.: username required, and password required.

    FIXME: ... I am however more and more inclined to make errors an dict where each key in the
    object is representative of an object ID and its error.

    Supplying the response status_code is pretty straightforward.
    Additional response headers should be irrelevant for now.

    Future improvements:
     - Support pagination
     - Support csv DL resposne types
     - Maybe support different serialization schemes
     - Ensure the given data arg is a list
      -- Maybe we pass in the marshmallow schema and the result set,
       perform the validation in the wrapper and return the response.
       Currently the caller has to do that....
    """
    def __init__(self):
        self.response = {
            "errors": [],
            "results": {
                "detail": "",
                "count": 0,
                "data": []
            }
        }
    
    def set_errors(self, errors):
        self.response.errors = errors

    def to_json(self, data=[], status_code=200, headers=None):        
        if len(self.response["errors"]) > 0:
            return jsonify(self.response), status_code, headers

        self.response["results"]["count"] = len(data)
        self.response["results"]["data"] = data
        return jsonify(self.response), status_code, headers
