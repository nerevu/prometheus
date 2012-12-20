from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.Development')
app.config.from_envvar('APP_SETTINGS', silent=True)

db = SQLAlchemy(app)

@app.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404

@app.template_filter()
def currency(x):
	try:
		return '$%.2f'%x
	except TypeError:
		return x

# app.jinja_env.filters['currency']=currency

# from app.cronus.views import cronus as cronusBp
from app.hermes.views import hermes as hermesBp
# from app.icarus.views import icarus as icarusBp
# from app.oracle.views import oracle as oracleBp
# app.register_blueprint(cronusBp)
app.register_blueprint(hermesBp)
# app.register_blueprint(icarusBp)
# app.register_blueprint(oracleBp)
