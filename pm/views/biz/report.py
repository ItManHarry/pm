from flask import Blueprint, current_app, render_template, url_for
from flask_login import login_required, current_user
from pm.decorators import log_record
bp_report = Blueprint('rpt', __name__)
@bp_report.route('/program', methods=['GET', 'POST'])
@login_required
@log_record('查看项目报表')
def program():
    return render_template('biz/report/program/index.html')
@bp_report.route('/issue', methods=['GET', 'POST'])
@login_required
@log_record('查看ISSUE报表')
def issue():
    return render_template('biz/report/issue/index.html')
