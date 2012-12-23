from __future__ import with_statement

from datetime import date
from datetime import datetime
from flask import json

dumps = json.dumps
loads = json.loads


class MainTestCase(TestCase):
	def test_empty_db(self):
		resp = self.client.get('/')
		assert '' in resp.data
