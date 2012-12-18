from setuptools import setup, find_packages

setup(
	name='Hermes',
	version='0.5',
	long_description=__doc__,
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	install_requires=['Flask', 'SQLAlchemy']
)
