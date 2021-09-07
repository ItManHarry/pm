from flask import Blueprint, render_template, session
from flask_login import login_required, current_user
bp_main = Blueprint('main', __name__)
@bp_main.route('/index')
@login_required
def index():
    # 清空session值
    session.pop('nav', None)
    session.pop('module_id', None)
    session.pop('menus', None)
    role = current_user.role
    return render_template('main/index.html')