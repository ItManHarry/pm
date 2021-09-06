from flask import Blueprint, render_template, session
from flask_login import login_required
bp_issue = Blueprint('iss', __name__)
@bp_issue.route('/index')
@login_required
def index():
    session['nav'] = 'iss'
    return 'OK'
    #return render_template('sys/index.html')