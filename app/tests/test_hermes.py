# -*- coding: utf-8 -*-
"""
	app.tests.test_hermes
	~~~~~~~~~~~~~~~~

	Provides unit tests for the :mod:`app.hermes` module.
"""

import nose.tools as nt

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
	print('Hermes Module Setup\n')
