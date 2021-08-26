from flask import Blueprint, render_template, session
from flask_login import login_required
bp_sys = Blueprint('sys', __name__)
@bp_sys.route('/index')
@login_required
def index():
    session['nav'] = 'sys'
    return render_template('sys/index.html')