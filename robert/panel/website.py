from flask import Blueprint, render_template


website = Blueprint('website', __name__)


@website.route('/')
def index():
    return render_template('index.html', items=['a', 'b', 'c'])
