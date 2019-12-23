TESS REST API - Transactive Energy Service System REST API

# Overview

This describes the resources that implement the TESS REST API v1.

## Version

By default, all requests to the API server receive `v1` version of the REST API.  All requests should explicitly request this version via the `Accept` header:

~~~
HTTP/1.1 GET /
Accept: application/vnd.tess-slacgismo.v1+json
~~~

## Schema

All API access is over HTTPS and accessed from the server, e.g., `https://tess.slacgismo.io/`.  All data is sent and received as JSON. 

Blank fields are included as `null` instead of being omitted.

All datetimes are returned in UTC ISO8601 format, e.g., `YYYY-MM-DDTHH:MM:SS.SSSSSSZ`. Timestamps are in float seconds since `1970-01-01T00:00:00.000000Z`.

### Summary responses

Some responses are lists of resources that are computationally costly to deliver. Only a subset of the attributes are delivered for those resources. For example, the request

~~~
HTTP/1.1 GET /price/{system}/{resource}
Range: timestamp=1577108100-1577194500
~~~

returns

~~~
HTTP/1.1 206 Partial Content
Content-Type: text/json
Content-Length: {body-length}
Content-Range: 1-288/576

[
	{
		"datetime" : "{timestamp}",
		"price" : "{price}"
	}
	{
		"datetime" : "{timestamp}",
		"price" : "{price}"
	}
	...
	{
		"datetime" : "{timestamp}",
		"price" : "{price}"
	}
]
~~~

### Detailed responses

When an individual resource is obtained, the response typically includes all the known attributed for that resource. For example, the request

~~~
HTTP/1.1 GET /price/my_system/capacity?quantity={quantity}
~~~

returns

~~~
HTTP/1.1 200 OK
Content-Type: text/json
Content-Length: {body-length}

{
	"system" : "{system}",
	"resource" : "{resource}",
	"datetime" : "{timestamp}",
	"quantity" : "{quantity}",
	"price" : "{price}",
	"margin" : "{margin}"
}
~~~

## Authentication

Only OAuth2 token authentication is supported:

~~~
HTTP/1.1 GET /
Authorization: token {token}
~~~

Requests that require authentication may return either `404 Not Found` or `403 Forbidden` depending on whether it is necessary to prevent accidental leakage of private information to unauthorized users.

## Failed Login Limits

Invalid credentials will return `401 Unauthorized`:

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
HTTP/1.1 GET /price/{system}/{resource}?order={order}
~~~

For `PUT` requests, parameters are specified using a body encoded in JSON with `Content-Type: application/json`:

~~~
HTTP/1.1 PUT /bid/{system}/{resource}

{
	"device" : "{device}",
	"quantity" : "{quantity}",
	"price" : "{price}",
}
~~~

## Query errors

API calls that use only a query string can result in two types of responses:

1. `406 Not Acceptable` - the request is not acceptable because a parameter is invalid, e.g.,

~~~
HTTP/1.1 406 Not Acceptable

{ 
	"message" : "Validation failed",
	"errors" : [
		{
			"endpoint" : "{endpoint}",
			"field" : "{field-name}",
			"code" : "not_found",
		}
	]
}
~~~

2. `422 Unprocessable Entity` - the request cannot be processed, i.e., a required parameter is missing, e.g.,

~~~
HTTP/1.1 422 Unprocessable Entity

{ 
	"message" : "Missing parameter",
	"errors" : [
		{
			"endpoint" : "{endpoint}",
			"field" : "{field-name}",
			"code" : "missing",
		}
	]
}
~~~


## Client errors

API calls that include a body can result in three types of responses:

1. `400 Bad Request` - the request is not formatted properly

~~~
HTTP/1.1 400 Bad Request

{ "message" : "JSON cannot be parsed" }
~~~

2. `406 Not Acceptable` - the request is not acceptable because a parameter is invalid, e.g.,

~~~
HTTP/1.1 406 Not Acceptable

{ 
	"message" : "Validation failed",
	"errors" : [
		{
			"endpoint" : "{endpoint}",
			"field" : "{field-name}",
			"code" : "not_found",
		}
	]
}
~~~

3. `422 Unprocessable Entity` - the request cannot be processed, i.e., a required parameter is missing, e.g.,

~~~
HTTP/1.1 422 Unprocessable Entity

{ 
	"message" : "Missing parameter",
	"errors" : [
		{
			"endpoint" : "{endpoint}",
			"field" : "{field-name}",
			"code" : "missing",
		}
	]
}
~~~

## HTTP redirects

API v1 uses HTTP redirection when necessary.  Clients should assume that a request may result in a redirection and should follow that redirect.  Redirect responses will have a `Location` header field when contains the URI of the resource to which the client should repeat the requests.

### Permanent redirects `301`

Permanent redirection. The URI used to make the request has been superseded by the one specified in the `Location` header field. This and all future requests to this resource should be directed to the new URI.

### Temporary redirects `302` and `307`

Temporary redirection. The request should be repeated verbatim to the URI specified in the `Location` header field but clients should continue to use the original URI for future requests.

## HTTP verbs

The API v1 uses the following HTTP verbs for actions.

### `GET`

The `GET` verb is used for retrieving price and quantity information.

### `PUT`

The `PUT` verb is used for create new bids.

### `DELETE`

The `DELETE` verb is used to delete an existing bids.

## Rate limiting

API requests using no authentication are limited to 60 requests per hour.  Authenticated requests are limited to 3600 requests per hour.  Valid requests that exceed the rate limit will receive the client error response 

~~~
HTTP/1.1 429 Too Many Requests

{
	"message" : "Rate limited",
	"limit" : "{rate-limit}",
	"reset_at" : "{datetime}",
} 
~~~

Clients that abuse the rate limiting system will be blocked and ignored without response.

## Time and page ranges

All queries may be accompanied by a time range to request responses limited to the time and page ranges given using the `Range` header attribute.

For time ranges, use `Range: timestamp={start}-{stop}`.

When more than `{page-limit}` values are returned, the response is paginated. In this case, the response header includes the following

~~~
Content-Range: page {start}-{stop}/{size}
~~~

To request a page, use the query header attribute `Range: page={start}` in addition to the `timestamp` range. To request a specific page range use the query header attribute `Range: page={start}-{stop}`.

# Endpoints

The TESS API interface supports the following endpoints.

## Root `/`

~~~
GET /
~~~

A `GET` request to the root endpoint gets all the endpoint support by the REST API.

### Response

~~~
{
	"config" : 
	{
		"hostname" : "https://tess.slacgismo.io/",
		"systems" : 
		[
			"{system}",
			"{system}",
			...
			"{system}
		],
		"limit" : "{limit}"
	}
	"order" : 
	{
		"URI" : "https://tess.slacgismo.io/",
		"PUT" : ["/{system}/{resource}"],
		"GET" : ["/{systems}/{resource}/{order}"],
		"DELETE" : ["/{systems}/{resource}/{order}"]
	},
	"price" :
	{
		"URI" : "https://tess.slacgismo.io/",
		"GET" : [
			"/{system}/{resource}?quantity={quantity}",
			"/{system}/{resource}?order={order}"
		]
	}
}
~~~

## Endpoint `/config`

~~~
GET /config/{system}
GET /config/{system}/{resource}
~~~

A `GET` request to the the `/config/{system}` endpoint returns the current configuration for `{system}`, e.g.,

~~~
{
	"resources" : [
		"{resource}",
		"{resource}",
		...
		"{resource}
	]
}
~~~

A `GET` request to the the `/config/{system}/{resource}` endpoint returns the current configuration for `{resource}` in `{system}`, e.g.,

~~~
{
	"interval" : {time-interval};
	"resource" : "{resource}",
	"units" : 
	{
		"time" : "{time-unit}";
		"currency" : "{current-unit}";
		"quantity" : "{quantity-unit}";
		"price" : "{price-unit}",
		"cost" : "{cost-unit}",
	}
}
~~~

## `/order` endpoint

~~~
PUT /order/{system}/{resource}
PUT /order/{system}/{resource}/{order}
GET /order/{system}/{resource}
GET /order/{system}/{resource}/{order}
DELETE /order/{system}/{resource}/{order}
~~~

The `order` endpoint adds/modifies (using `PUT`) an order or retrieves (using `GET`) an existing order for `{resource}` in `{system}`. 

### Query

The request body for submitted a new order (using `PUT`) is of the form

~~~
PUT /order/{system}/{resource}

{
	"device" : "{device}",
	"quantity" : "{quantity}",
	"price" : "{price}",
	"duration" : "{duration}",
	"current" : "{current}",
	"allow_margin" : "{margin-ok}"
}
~~~

If the request body includes the `{order}`, the order is modified.

~~~
PUT /order/{system}/{resource}/{order}

{
	"device" : "{device}",
	"quantity" : "{quantity}",
	"price" : "{price}",
	"duration" : "{duration}",
	"current" : "{current}",
	"allow_margin" : "{margin-ok}"
}
~~~

A new order using `PUT` must include the `device`, and `quantity` fields.  A negative `quantity` indicates a `sell` or `ask` bid, and a positive `quantity` indicates a `buy` or `offer` bid. 

If the `price` is absent, the order is a *price taker* meaning that the order will be filled at the best available price. An order that includes the `price` field indicates a reservation price is available, and the order will only be filled if the price is matched or better.

A bid that includes the `duration` field indicates the duration for which the device will operate if the bid clears. This is only meaning in `orderbook` markets.

A value of `current` indicates that the device is currently operating with a `quantity` different from the `bid` quantity. This is only meaning in `auction` markets.

| Field name | Required | Remark                                      |
| ---------- | :------: | ------------------------------------------- |
| `device`   | Always   | Must be a known device                      |
| `quantity` | `POST`   | Must be strictly position or negative       |
| `price`    |  -       | Indicates price is reserved                 |
| `duration` |  -       | Indicates the operation duration is limited |
| `current`  |  -       | Indicates the current quantity is different |

The request query string for retrieving a list of open orders is

~~~
GET /order/{system}/{resource}
~~~

This will retrieve a list of all the open orders for `{resource}` on `{system}`.

If `{order}` is included, the specific order is retrieved:

~~~
GET /order/{system}/{resource}/{order}
~~~

This will retrieve the same data as originally returned by the `PUT` query submitted. If the order is cleared, the `price` and `margin` attributed will also be included.  If the order was not filled immediately, the `clear` field will be included.

To delete an order, use the query

~~~
DELETE /order/{system}/{resource}/{order}
~~~

### Response

The response to a `PUT` will always include `order` and either a `price` or `clear`. If the `PUT` body does not include a `price` attribute and it can be immediately filled, the response is `200 OK`:

~~~
{
	"order" : "{order}",
	"price" : "{price}",
	"margin" : "{margin}",
}
~~~

where `{order}` is the order id, `{price}` is the cleared price at which the order was filled, and `{margin}` is the fraction of the order that was filled, if the order was not fully filled. If `margin` is absent, the order was completely cleared.

If the order cannot be filled immediately, the response is `202 Accepted`:

~~~
{
	"order" : "{order}",
	"clear" : "{clearing-time}"
}
~~~

where `{clearing-time}` is the time at which the order is expected to be filled and a price will be available for the order.  

If one of the required fields is missing, the response is `422 Unprocessable Entity`:

~~~
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

If a field is invalid the response is `422 Unprocessable Entity`:

~~~
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

The response to a `GET` query for a list of orders is

~~~
{
	"{order}" :
	{
		"price" : "{price}",
		"quantity" : "{quantity}"
	},
	"{order}" :
	{
		"price" : "{price}",
		"quantity" : "{quantity}"
	},
	...
	"{order}" :
	{
		"price" : "{price}",
		"quantity" : "{quantity}"
	}
}
~~~

The `DELETE` query always gives the response `204 No Content` when successful.

## `/price` endpoint

~~~
GET /price/{system}/{resource}
GET /price/{system}/{resource}?quantity={quantity}
GET /price/{system}/{resource}?order={order}
~~~

The `price` endpoint is used to obtain the current price. These may be requested for a given quantity or an outstanding order.

### Response

~~~
{
	"datetime" : "{datetime}",
	"order" : "{int}",
	"resource" : "{str}",
	"price" : "{float}",
	"margin" : "{float}"
	}
}
~~~

If a time range is given in the header, the response will be a list:

~~~
[
	"{datetime}" : {
		"price" : "{price}",
		"quantity" : "{quantity}",
		"margin" : "{margin}"
	},
	"{datetime}" : {
		"price" : "{price}",
		"quantity" : "{quantity}",
		"margin" : "{margin}"
	},
	...
	"{datetime}" : {
		"price" : "{price}",
		"quantity" : "{quantity}",
		"margin" : "{margin}"
	}
]
~~~

