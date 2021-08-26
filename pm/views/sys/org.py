'''
系统部门信息管理
'''
from flask import Blueprint, render_template
from flask_login import login_required
bp_org = Blueprint('org', __name__)
@bp_org.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('sys/org/index.html')
