from flask import render_template
from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def home():
	return render_template('main/hero.html')

