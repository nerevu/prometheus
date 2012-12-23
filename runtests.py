#!/usr/bin/env python
import unittest2
from app.tests import suite


def main():
    unittest2.main(defaultTest='suite')

if __name__ == '__main__':
    main()
