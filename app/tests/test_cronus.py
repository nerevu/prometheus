# -*- coding: utf-8 -*-
"""
	app.tests.test_cronus
	~~~~~~~~~~~~~~~~

	Provides unit tests for the :mod:`app.cronus` module.
"""

import nose.tools as nt

from os import path as p
from . import get_globals, check_equal, loads, err
from pprint import pprint
from app import create_app


def setup_module():
	"""site initialization"""
	global initialized
	global content

	values = get_init_values()
	content = conn.process(values)
	initialized = True
	print('Cronus Module Setup\n')
