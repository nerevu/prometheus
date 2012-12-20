from flask import render_template
from flask import Blueprint

main = Blueprint('main', __name__)

def get_assets(template):
	all_js = [
		'bootstrap-transition.js',
		'bootstrap-alert.js',
		'bootstrap-modal.js',
		'bootstrap-dropdown.js',
		'bootstrap-scrollspy.js',
		'bootstrap-tab.js',
		'bootstrap-tooltip.js',
		'bootstrap-popover.js',
		'bootstrap-button.js',
		'bootstrap-collapse.js',
		'bootstrap-carousel.js',
		'bootstrap-typeahead.js',]

	assets = {'template': template, 'css': 'sticky.css', 'js': None}
	print(assets['template'])
	return assets

@main.route('/', methods=['GET', 'POST'])
def home():
	s = get_assets('sticky')
# 	return render_template(s['template'], css=s['css'], js=s['js'])
	return render_template('main/hero.html')

