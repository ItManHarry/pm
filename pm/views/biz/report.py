from flask import Blueprint, current_app, render_template, url_for, request
from flask_login import login_required, current_user
from pm.models import BizProgram
from pm.forms.biz.program import ProgramSearchForm
from pm.decorators import log_record
bp_report = Blueprint('rpt', __name__)
@bp_report.route('/program', methods=['GET', 'POST'])
@login_required
@log_record('查看项目报表')
def program():
    no = ''  # 项目编号
    name = ''  # 项目名称
    form = ProgramSearchForm()
    if request.method == 'POST':
        no = form.no.data
        name = form.name.data
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    pagination = BizProgram.query.filter(BizProgram.no.like('%' + no + '%'), BizProgram.name.like('%' + name + '%')).order_by(BizProgram.timestamp_loc).paginate(page, per_page)
    programs = pagination.items
    return render_template('biz/report/program/index.html', form=form, programs=programs, pagination=pagination)
@bp_report.route('/issue', methods=['GET', 'POST'])
@login_required
@log_record('查看ISSUE报表')
def issue():
    return render_template('biz/report/issue/index.html')
