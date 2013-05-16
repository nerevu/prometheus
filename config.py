import os
from os import path as p
from datetime import date as d

_basedir = p.dirname(__file__)

# change these values
__APP_NAME__ = 'Prometheus'
__YOUR_NAME__ = 'Reuben Cummings'
__YOUR_EMAIL__ = 'reubano@gmail.com'
__YOUR_WEBSITE__ = 'http://reubano.github.com'


# configuration
class Content(object):
	app = __APP_NAME__.lower()

	site_values = (
		app, __APP_NAME__, __YOUR_NAME__,
		__YOUR_WEBSITE__, 'home')

	topnav_values = [
		('price', 'Prices', 'hermes.get', 'price'),
		('event', 'Events', 'hermes.get', 'event'),
		('transaction', 'Transactions', 'cronus.transaction', None),
		('worth', 'Net Worth', 'apollo.worth', 'USD'),
		('about', 'About', 'about', None),
		('api', 'API', 'api', None)]

	hero_values = (
		'%s: a global asset allocation tool', '%s is'
		' a full featured web app that tells you how your stock portfolio has '
		' performed over time, gives insight into how to optimize your asset '
		' allocation, and monitors your portfolio for rebalancing or performance'
		' enhancing opportunities.' % __APP_NAME__, 'about')

	sub_unit_values = [
		(
			'Events', 'See all your stocks events in one convenient'
			' location. Track stock splits, dividend payments,'
			' mergers and more!', 'hermes.get', 'event'),
		(
			'Transactions', 'Add your stock transactions with the click of a '
			'button! CSV file upload feature coming soon.',
			'cronus.transaction', None),
		(
			'Net Worth', 'See how the value of your portfolio changed over '
			'time with these sleek interactive charts! Instantly see how  '
			'dividends impact your return.', 'apollo.worth', 'USD')]

	mkd_values = [('about', 'about.md'), ('api', 'api.md')]
	total_site_values = site_values + (
		d.today().strftime("%Y"), 12 / len(sub_unit_values))

	site_keys = (
		'id', 'caption', 'author', 'author_url', 'location', 'date', 'sub_span')
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
	stage = os.environ.get('STAGE', False)
	end = '-stage' if stage else ''
	heroku = os.environ.get('DATABASE_URL', False)  # change this

	DEBUG = False
	ADMINS = frozenset([__YOUR_EMAIL__])
	TESTING = False
	HOST = '127.0.0.1'
	heroku_server = '%s%s.herokuapp.com' % (Content.app, end)

	# change this if you host your own api
	api_base = 'http://prometheus-api.herokuapp.com'

	if heroku:
		SERVER_NAME = heroku_server

	api_prefix = ''
	API_URL = api_base + '/' + api_prefix if api_prefix else api_base
	SECRET_KEY = os.environ.get('SECRET_KEY', 'secret_key')
	CSRF_SESSION_KEY = os.environ.get('CSRF_SESSION_KEY', 'secret_key')
	RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', 'secret_key')
	RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', 'secret_key')
	BOOTSTRAP_USE_MINIFIED = True
	BOOTSTRAP_USE_CDN = False
	BOOTSTRAP_FONTAWESOME = False
	BOOTSTRAP_HTML5_SHIM = True
	BOOTSTRAP_GOOGLE_ANALYTICS_ACCOUNT = os.environ.get(
		'GOOGLE_ANALYTICS_ID', '')

	CSRF_ENABLED = True
	RECAPTCHA_USE_SSL = False
	RECAPTCHA_OPTIONS = {'theme': 'white'}


class Production(Config):
	HOST = '0.0.0.0'
	BOOTSTRAP_USE_CDN = True
	BOOTSTRAP_FONTAWESOME = True


class Development(Config):
	DEBUG = True


class Test(Config):
	TESTING = True
