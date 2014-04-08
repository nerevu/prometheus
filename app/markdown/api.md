---
heading: The Prometheus ReSTful API
subheading: Learn how to query and update Prometheus using the ReSTful API
---

## Endpoints

The Prometheus API has endpoints located at `http://prometheus-api.herokuapp.com/api/<table>`. Currently accesible tables include the following:

* [exchange](http://prometheus-api.herokuapp.com/api/exchange)
* [data_source](http://prometheus-api.herokuapp.com/api/data_source)
* [commodity_group](http://prometheus-api.herokuapp.com/api/commodity_group)
* [commodity_type](http://prometheus-api.herokuapp.com/api/commodity_type)
* [commodity](http://prometheus-api.herokuapp.com/api/commodity)
* [event_type](http://prometheus-api.herokuapp.com/api/event_type)
* [price](http://prometheus-api.herokuapp.com/api/price)

- - -

## Methods

The API is a ReSTful service and allows the following HTTP methods:

* GET
* DELETE
* POST
* PATCH
* PUT

- - -

## Examples

Data is sent and received through the API endpoints in JSON format. Below are python usage examples.

_initial setup_

	import json
	import requests

	headers = {'content-type': 'application/json'}
	site = 'http://prometheus-api.herokuapp.com/api'

_get request_

	r = requests.get('%s/event_type' % site, headers=headers)
	r.status_code, r.json

_post request_

	newsource = {'name': 'Yahoo'}
	r = requests.post('%s/data_source' % site, data=json.dumps(newsource), headers=headers)
	r.status_code, r.json

_patch request_

	patch = {'type': {'add': {'name': 'New Type', 'group_id': 2}}}
	r = requests.patch('%s/commodity/1' % site, data=json.dumps(patch), headers=headers)
	r.status_code, r.json

_delete request_

	r = requests.delete('%s/commodity_type/1' % site, headers=headers)
	r.status_code, r.json
