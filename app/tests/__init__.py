# -*- coding: utf-8 -*-
"""
	app.tests
	~~~~~~~~~~~~~~

	Provides application unit tests
"""

import sys
import nose.tools as nt

from flask import json
from app import create_app
from requests import get, post, delete, patch

loads = json.loads
dumps = json.dumps
err = sys.stderr
initialized = False


def setup_package():
	"""database context creation"""
	global initialized
	global app
	global client
	global jsonx
	global base

	app = create_app(config_mode='Test')
	base = app.config['API_URL']
	client = app.test_client()
	jsonx = app.test_request_context()
	jsonx.push()
	initialized = True

	print('Test Package Setup\n')


def teardown_package():
	"""database context removal"""
	global initialized
	global jsonx

	jsonx.pop()
	initialized = False

	print('Test Package Teardown\n')


def check_equal(page, x, y):
	nt.assert_equal(x, y)


def get_globals():
	global app
	global client
	global jsonx

	return app, client, jsonx
