from os import path as p

_basedir = p.abspath(p.dirname(__file__))


# configuration
class Config(object):
	DEBUG = False
	ADMINS = frozenset(['email@ydomain.com'])
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


class Testing(Config):
	SQLALCHEMY_DATABASE_URI = 'sqlite://:memory:'
	TESTING = True
