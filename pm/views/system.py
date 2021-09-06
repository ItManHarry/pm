from flask import Blueprint, render_template, session
from flask_login import login_required
bp_sys = Blueprint('sys', __name__)
@bp_sys.route('/index')
@login_required
def index():
    session['nav'] = 'sys'
    # 获取菜单权限

    return render_template('sys/index.html')