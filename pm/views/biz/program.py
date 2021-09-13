from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required, current_user
from pm.forms.biz.program import ProgramForm, ProgramSearchForm, ProgramMemberForm
from pm.models import BizProgram, SysDict, SysUser, BizProgramMember, BizDept
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
@bp_pro.route('/members/<pro_id>')
@login_required
@log_record('管理项目成员')
def members(pro_id):
    form = ProgramMemberForm()
    form.pro_id.data = pro_id
    program = BizProgram.query.get_or_404(pro_id)
    # 部门信息
    all_dept = BizDept.query.order_by(BizDept.code).all()
    departments = []
    for dept in all_dept:
        departments.append((dept.id, dept.name))
    dept_id = departments[0][0]
    form.user_dept.choices = departments
    # 项目成员角色字典
    dictionary = SysDict.query.filter_by(code='D002').first()
    enums = dictionary.enums
    pro_roles = []
    for enum in enums:
        pro_roles.append((enum.id, enum.display))
    enum_id = pro_roles[0][0]
    form.pro_roles.choices = pro_roles
    # 已选成员
    pro_members = program.members
    selected_ids = []               # 已选人员ID(用于过滤可选成员)
    selected = [(1, 1), (2, 2)]     # 已选人员(用于列表显示)
    form.pro_roles.data = enum_id
    for pro_member in pro_members:
        selected_ids.append(pro_member.member.id)
        selected.append((pro_member.member.id, pro_member.member.name))
    form.selected.choices = selected
    # 可选成员
    all_users = SysUser.query.with_parent(BizDept.query.get(dept_id)).all()
    for_select = []
    for user in all_users:
        if user.user_id != 'admin' and user.user_id not in selected_ids: # 除去管理员及已添加人员
            for_select.append((user.id, user.user_name))
    form.for_select.choices = for_select
    return render_template('biz/program/members.html', form=form, program=program)