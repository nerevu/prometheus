try:
	from setuptools import setup, find_packages
except ImportError:
	from distutils.core import setup, find_packages


with open('../requirements.txt') as file:
	requirements = file.read()


config = {
	'name': 'prometheus',
	'description': 'a global asset allocation tool',
	'long_description': open('README.rst', 'rt').read(),
	'author': 'Reuben Cummings',
	'url': 'https://github.com/reubano/prometheus',
	'download_url':
		'https://github.com/reubano/prometheus/downloads/prometheus*.tgz',
	'author_email': 'reubano@gmail.com',
	'version': '0.14.0',
	'install_requires': requirements.split('\n'),
	'classifiers': ['Development Status :: 4 - Beta',
		'License :: OSI Approved :: The MIT License (MIT)',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Operating System :: MacOS :: MacOS X',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: Microsoft :: POSIX'],
	'packages': find_packages(),
	'zip_safe': False,
	'license': 'MIT',
    'platforms': ['MacOS X', 'Windows', 'Linux'],
	'include_package_data': True,
}

setup(**config)
