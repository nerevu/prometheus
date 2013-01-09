from os import path as p
from datetime import date as d

_basedir = p.dirname(__file__)


# configuration
class Content(object):
	site_values = ('prometheus', 'Prometheus', 'Reuben Cummings',
		'http://reubano.github.com', 'home')

	topnav_values = [('event', 'Events', 'hermes.get', 'event'),
		('event_type', 'Types', 'hermes.get', 'event_type'),
		('price', 'Prices', 'hermes.get', 'price'),
		('commodity', 'Commodities', 'hermes.get', 'commodity'),
		('worth', 'Net Worth', 'apollo.worth', 'USD'),
		('about', 'About', 'about', None),
		('api', 'API', 'api', None)]

	hero_values = ('Prometheus: a global asset allocation tool', 'Prometheus is'
		' a full featured web app that tells you how your stock portfolio has '
		' performed over time, gives insight into how to optimize your asset '
		' allocation, and monitors your portfolio for rebalancing or performance'
		' enhancing opportunities.', 'about')

	sub_unit_values = [('Events', 'See all your stocks events in one convenient'
		' location. Track stock splits, dividend payments, mergers and more!',
		'hermes.get', 'event'),
		('Prices', 'Update your stock prices with the click of a button! '
		'Automatically grap the latest pricing information from Yahoo or '
		'Google.', 'hermes.get', 'price'),
		('Net Worth', 'See how the value of your portfolio changed over time '
		'with these sleek interactive charts! Instantly see how dividends '
		'impact your return.', 'apollo.worth', 'USD')]

	mkd_values = [('about', 'about.md'), ('api', 'api.md')]
	total_site_values = site_values + (d.today().strftime("%Y"),
		12 / len(sub_unit_values))

	site_keys = ('id', 'caption', 'author', 'author_url', 'location', 'date',
		'sub_span')
	topnav_keys = ('id', 'caption', 'location', 'table')
	hero_keys = ('heading', 'subheading', 'location')
	sub_unit_keys = ('heading', 'text', 'location', 'table')
	mkd_keys = ('id', 'file')

	SITE = dict(zip(site_keys, total_site_values))
	TOPNAV = [dict(zip(topnav_keys, values)) for values in topnav_values]
	HERO = dict(zip(hero_keys, hero_values))
	SUB_UNITS = [dict(zip(sub_unit_keys, values)) for values in sub_unit_values]
	MKD_PAGES = [dict(zip(mkd_keys, values)) for values in mkd_values]
	MKD_FOLDER = 'markdown'


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
