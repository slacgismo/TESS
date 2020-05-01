from flask import jsonify

class ApiResponseWrapper(object):
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
        """
        Data and Errors are mutually exclusive on the response
        """
        if len(self.response["errors"]) > 0:
            return jsonify(self.response), status_code, headers

        self.response["results"]["count"] = len(data)
        self.response["results"]["data"] = data
        return jsonify(self.response), status_code, headers
