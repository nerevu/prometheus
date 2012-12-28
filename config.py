from os import path as p
from datetime import date as d

_basedir = p.abspath(p.dirname(__file__))


# configuration
class Content(object):
# 	MODULES = ['main', 'hermes']
	TOPNAV = [{'id': 'event', 'caption': 'Events', 'location': 'hermes.get',
		'table': 'event'}, {'id': 'event_type', 'caption': 'Types',
		'location': 'hermes.get', 'table': 'event_type'}, {'id': 'price',
		'caption': 'Prices', 'location': 'hermes.get', 'table': 'price'},
		{'id': 'commodity', 'caption': 'Commodities',
		'location': 'hermes.get', 'table': 'commodity'},
		{'id': 'worth', 'caption': 'Net Worth', 'location': 'hermes.worth'}]

	HERO = {'heading': 'Prometheus: a global asset allocation tool',
		'text': 'Prometheus is a full featured web app that tells you how your'
		' stock portfolio has performed over time, gives insight into how to '
		'optimize your asset allocation, and monitors your portfolio for '
		'rebalancing or performing enhancing opportunities.'}

	SUB_UNITS = [{'heading': 'Events', 'text': 'See all your stocks events in '
		'one convenient location. Track stock splits, dividend payments, '
		'mergers and more!', 'location': 'hermes.get', 'table': 'event'},
		{'heading': 'Prices', 'text': 'Update your stock prices with the click'
		' of a button! Automatically grap the latest pricing information from '
		'Yahoo or Google.', 'location': 'hermes.get', 'table': 'price'},
		{'heading': 'Net Worth', 'text': 'See how the value of your portfolio '
		'over time with these sleek interactive charts! Instantly see how the '
		'effects of dividends impacts your return.',
		'location': 'hermes.worth'}]

	SITE = {'id': 'prometheus', 'caption': 'Prometheus',
		'date': d.today().strftime("%Y"), 'author': 'Reuben Cummings',
		'author_url': 'http://reubano.github.com',
		'sub_span': 12 / len(SUB_UNITS), 'location': 'home'}


class Config(Content):
	DEBUG = False
	ADMINS = frozenset(['reubano@gmail.com'])
	TESTING = False
	SECRET_KEY = 'secret_key'
	BOOTSTRAP_USE_MINIFIED = True
	BOOTSTRAP_USE_CDN = False
	BOOTSTRAP_FONTAWESOME = False
	BOOTSTRAP_HTML5_SHIM = True
	BOOTSTRAP_GOOGLE_ANALYTICS_ACCOUNT = ''
	CSRF_ENABLED = True
	CSRF_SESSION_KEY = 'csrf_session_key2'
	RECAPTCHA_USE_SSL = False
	RECAPTCHA_PUBLIC_KEY = 'recaptcha_public_key'
	RECAPTCHA_PRIVATE_KEY = 'recaptcha_private_key'
	RECAPTCHA_OPTIONS = {'theme': 'white'}
	API_METHODS = ['GET', 'POST', 'DELETE', 'PATCH', 'PUT']
	API_ALLOW_FUNCTIONS = True
	API_ALLOW_PATCH_MANY = True


class Production(Config):
	SQLALCHEMY_DATABASE_URI = 'mysql://user@localhost/foo'
	HOST = '0.0.0.0'
	BOOTSTRAP_USE_CDN = True
	BOOTSTRAP_FONTAWESOME = True


class Development(Config):
	SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % p.join(_basedir, 'app.db')
	DEBUG = True


class Test(Config):
	SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

	TESTING = True
