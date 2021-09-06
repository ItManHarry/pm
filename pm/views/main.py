from flask import Blueprint, render_template
from flask_login import login_required, current_user
bp_main = Blueprint('main', __name__)
@bp_main.route('/index')
@login_required
def index():
    role = current_user.role
    print('Role ', role.name)
    return render_template('main/index.html')