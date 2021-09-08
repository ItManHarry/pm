from flask import Blueprint, render_template, session, url_for, request, current_app
from flask_login import login_required, current_user
from pm.forms.biz.program import ProgramForm, ProgramSearchForm
from pm.models import BizProgram
from pm.plugins import db
from pm.decorators import log_record
bp_pro = Blueprint('pro', __name__)
@bp_pro.route('/index')
@login_required
@log_record('查看项目清单')
def index():
    no = ''     # 项目编号
    name = ''   # 项目名称
    form = ProgramSearchForm()
    if request.method == 'POST':
        no = form.no.data
        name = form.name.data
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    pagination = BizProgram.query.with_parent(current_user).filter(BizProgram.no.like('%' + no + '%'), BizProgram.name.like('%' + name + '%')).order_by(BizProgram.timestamp_loc).paginate(page, per_page)
    programs = pagination.items
    return render_template('biz/program/index.html', form=form, programs=programs, pagination=pagination)