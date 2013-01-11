# -*- coding: utf-8 -*-
"""
	app.tests
	~~~~~~~~~~~~~~

	Provides application unit tests
"""

from unittest import TestCase
from app import create_app, db


class PackageCase(TestCase):
	def setUpPackage(self):
		"""database context creation"""
		self.app = create_app(config_mode='Test')
		self.client = self.app.test_client()
		self.jsonx = self.app.test_request_context()
		self.jsonx.push()

	def tearDownPackage(self):
		"""database context removal"""
		self.jsonx.pop()
