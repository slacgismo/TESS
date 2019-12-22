TESS REST API - Transactive Energy Service System REST API

# Overview

This describes the resources that implement the TESS REST API v1.

## Version

By default, all requests to the API server receive `v1` version of the REST API.  All requests should explicitly request this version via the `Accept` header:

~~~
Accept: application/vnd.tess.v1+json
~~~

## Schema

All API access is over HTTPS and accessed from the server, e.g., `https://localhost:8000/`.  All data is sent and received as JSON. 

Blank fields are included as `null` instead of being omitted. A

All timestamps are returned in UTC ISO8601 format, e.g., `YYYY-MM_DDTHH:MM:SSZ`.

## Authentication

Only OAuth2 token authentication is supported:

~~~
curl -H "Authorization: token <oauth-token>" https://localhost:8000/
~~~

Requests that require authentication may return either `404 Not Found` or `403 Forbidden` depending on whether it is necessary to prevent accidental leakage of private information to unauthorized users.

## Failed Login Limits

Invalid credential will return `401 Unauthorized`:

~~~
HTTP/1.1 401 Unauthorized
{
	"message" : "Bad credentials",
	"documentation_url" : "https://docs.slacgismo.org/TESS/v1"
}
~~~

## Parameters

Most API methods take optional parameters. For `GET` and `DELETE` requests, parameters are specified in HTTP query string:

~~~
curl https://localhost:8000/price?system=my_system&resource=capacity
~~~

For `POST` requests, parameters are specified using a body encoded in JSON with `Content-Type: application/json`:

~~~
HTTP/1.1 POST /bid
{
	"system" : "my_system",
	"device" : "d5255d6d96294ac79d81290c8a6c397e",
	"quantity" : "12.4",
	"price" : "0.24",
}
~~~

## Client errors

API calls that include a body can result in three types of responses:

1. `400 Bad Request` - request is not formatted properly

~~~
{ "message" : "JSON cannot be parsed" }
~~~

2. `406 Not Acceptable` - the request is not acceptable because a parameter is invalid, e.g.,

{ 
	"message" : "Validation failed",
	"errors" : [
		{
			"endpoint" : "bid",
			"field" : "system",
			"code" : "not_found",
		}
	]
}

3. `422 Unprocessable Entity` - the request cannot be processed, i.e., a required parameter is missing, e.g.,

~~~
{ 
	"message" : "Missing parameter",
	"errors" : [
		{
			"endpoint" : "bid",
			"field" : "system",
			"code" : "missing",
		}
	]
}
~~~

## HTTP redirects

API v1 uses HTTP redirection when necessary.  Clients should assume that any request may result in a redirection and should follow that redirect.  Redirect responses will have a `Location` header field when contains the URI of the resource to which the client should repeat the requests.

### Permanent redirects `301`

Permanent redirection. The URI you used to make the request has been superseded by the one specified in the Location header field. This and all future requests to this resource should be directed to the new URI.

### Temporary redirects `302` and `307`

Temporary redirection. The request should be repeated verbatim to the URI specified in the Location header field but clients should continue to use the original URI for future requests.

## HTTP verbs

The API v1 uses the following HTTP verbs for actions.

### `GET`

The `GET` verb is used for retrieving price and quantity information.

### `POST`

The `POST` verb is used for create new bids.

### `PATCH`

The `PATCH` verb is used to modify an existing bid.

### `DELETE`

The `DELETE` verb is used to delete an existing bids.

## Rate limiting

API requests using no authentication are limited to 60 requests per hour.  Authenticated requests are limited to to 3600 requests per hour.  Valid requests that exceed the rate limit will receive the client error response 

~~~
HTTP/1.1 429 Too Many Requests
{
	"message" : "Rate limited",
	"limit" : "50",
	"reset_at" : "2020-01-01T00:00:00Z",
} 
~~~

# Market

The market interface supports the following endpoints.

## `/` endpoint

~~~
GET /
~~~

A `get` request to the root endpoint gets all the endpoint support by the REST API.

### Response

~~~
{
	"bid_url" : "<str>",
	"price_url" : "<str>",
	"delete_url" : "<str>",
}
~~~

### Example

~~~
bash$ curl https://localhost:8000/
{
	"bid_url" : "https://localhost:8000/bid/{system}?resource={resource}"
	"price_url" : "https://localhost:8000/price/{system}"
}
~~~

## `/order` endpoint

~~~
POST /bid/{system}/{resource}
PATCH /bid/{system}/{resource}
~~~

The `bid` endpoint adds (using `POST`) a new bid or modifies (using `PATCH`) an existing bid for `{resource}` in `{system}`. 

### Body

The request body for a new bid (using `POST`) is of the form

~~~
HTTP/1.1 201 Created
{
	"device" : "<device-id>",
	"quantity" : "<float>",
	"price" : "<float>",
}
~~~

The request body for a bid modification (using `PATCH`) is of the form

~~~
HTTP/1.1 200 OK
{
	"order" : "<str>",
	"device" : "<int>",
	"quantity" : "<float>",
	"price" : "<float>",
	"duration" : "<float>",
	"current" : "<float>",
}
~~~

A new bid (using `POST`) must include the `device`, and `quantity` fields.  A negative `quantity` indicates a `sell` or `ask` bid, and a positive `quantity` indicates a `buy` or `offer` bid. 

A changed bid (using `PATCH`) must include the `order` field, and 

A bid that includes the `price` field indicates a reservation bid. If the `price` is absent, the bid is a *price taker* meaning that the device will supply or consume at any price.  

A bid that includes the `duration` field indicates the duration for which the device will operate if the bid clears. This is only meaning in `orderbook` markets.

A value of `current` indicates that the device is currently operating with a `quantity` different from the `bid` quantity. This is only meaning in `auction` markets.

| Field name | Required | Remark                                      |
| ---------- | :------: | ------------------------------------------- |
| `device`   | Always   | Must be a known device                      |
| `order`    | `PATCH`  | Required when using `PATCH`                 |
| `quantity` | `POST`   | Must be strictly position or negative       |
| `price`    |  -       | Indicates price is reserved                 |
| `duration` |  -       | Indicates the operation duration is limited |
| `current`  |  -       | Indicates the current quantity is different |

### Response

The response price include the order id and clearing time.

~~~
{
	"order" : "<str>",
	"clear" : "<datetime>"
}
~~~

If one of the required fields is missing, the response is

~~~
HTTP/1.1 422 Unprocessable Entity
{
	"message" : "Missing parameter",
	"errors" : [
		{
			"endpoint" : "bid",
			"field" : "<field-name>",
			"code" : "missing",
		}
	]

}
~~~

If a field is invalid the response is 

~~~
HTTP/1.1 422 Unprocessable Entity
{
	"message" : "Invalid parameter",
	"errors" : [
		{
			"endpoint" : "bid",
			"field" : "<field-name>",
			"code" : "<failure-code>",
		}
	]

}
~~~

The following failures modes are verified on the fields

| Field name | Condition | Failure code |
| ---------- | --------- | ------------ |
| `system` | `!exist` | `not_found` |
| `order`| `!exist` | `not_found` |
| `resource` | `!exist` | `not_found` |
| `device` | `!exist` | `not_found` |
| `quantity` | `!float` | `not_numeric` |
| `quantity` | `==0.0` | `is_zero` |
| `quantity` | `!float` | `not_numeric` |
| `price` | `<0.0` | `is_negative` |
| `price` | `!float` | `not_numeric` |
| `duration` | `<=0` | `not_positive` |
| `duration` | `!float` | `not_numeric` |
| `current` | `!float` | `not_numeric` |


## `/price` endpoint

~~~
GET /price/{system}/{resource}?quantity=<float>
GET /price/{system}/{resource}?order=<order>
~~~

The `price` endpoint is used to obtain the price for a given quantity or an outstanding order.

### Response

~~~
{
	"datetime" : "<datetime>",
	"order" : "<int>",
	"resource" : "<str>",
	"price" : "<float>",
	"margin" : "<float>"
	}
}
~~~

## `/order` endpoint

~~~
GET /order/{order-id}
DELETE /order/{order-id}
~~~

The `order` endpoint is use to access an order. The `DELETE` verb removes the order from the system and the `GET` verb retrieves the order status.

### Response

For `GET` action, the response is

~~~
HTTP/1.1 200 OK
{
	"system" : "<system-name>",
	"resource" : "<resource-type>",
	"order" : "<order-id>",
	"device" : "<device-id>",
	"quantity" : "<float>",
	"price" : "<float>",
	"duration" : "<float>",
	"current" : "<float>",
}
~~~

For `DELETE` action, the response is
~~~
HTTP/1.1 204 No Content
~~~
