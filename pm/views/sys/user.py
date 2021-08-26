'''
系统用户信息管理
'''
from flask import Blueprint, render_template
from flask_login import login_required
bp_user = Blueprint('user', __name__)
@bp_user.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('sys/users/index.html')