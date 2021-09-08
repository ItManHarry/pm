from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required, current_user
from pm.forms.biz.program import ProgramForm, ProgramSearchForm
from pm.models import BizProgram
from pm.plugins import db
from pm.decorators import log_record
from pm.utils import get_date
import uuid, random
bp_pro = Blueprint('pro', __name__)
@bp_pro.route('/index', methods=['GET', 'POST'])
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
@bp_pro.route('/add', methods=['GET', 'POST'])
@login_required
@log_record('新增项目')
def add():
    form = ProgramForm()
    if form.validate_on_submit():
        program = BizProgram(
            id=uuid.uuid4().hex,
            no='PRO' + get_date() + str(random.randint(1000, 9999)),
            name=form.name.data,
            pr=form.pr.data,
            contract=form.contract.data,
            desc=form.desc.data,
            svn=form.svn.data,
            owner=current_user,
            operator_id=current_user.id
        )
        db.session.add(program)
        db.session.commit()
        flash('项目添加成功！')
        return redirect(url_for('.add'))
    return render_template('biz/program/add.html', form=form)
@bp_pro.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
@log_record('修改项目信息')
def edit(id):
    form = ProgramForm()
    program = BizProgram.query.get_or_404(id)
    if request.method == 'GET':
        form.id.data = program.id
        form.no.data = program.no
        form.name.data = program.name
        form.pr.data = program.pr
        form.contract.data = program.contract
        form.svn.data = program.svn
        form.desc.data = program.desc
    if form.validate_on_submit():
        program.name = form.name.data
        program.pr = form.pr.data
        program.contract = form.contract.data
        program.svn = form.svn.data
        program.desc = form.desc.data
        program.operator_id = current_user.id
        db.session.commit()
        flash('项目信息更新成功！')
        return redirect(url_for('.edit', id=form.id.data))
    return render_template('biz/program/edit.html', form=form)