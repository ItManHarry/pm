from flask import Blueprint, render_template, session
from flask_login import login_required
bp_pro = Blueprint('pro', __name__)
@bp_pro.route('/index')
@login_required
def index():
    session['nav'] = 'pro'
    return 'OK'
    #return render_template('sys/index.html')