from unittest2 import TestSuite
from unittest2 import defaultTestLoader

from . import test_hermes


def suite():
    """Returns the test suite for this module."""
    result = TestSuite()
    loader = defaultTestLoader
    result.addTest(loader.loadTestsFromModule(test_hermes))
    return result
