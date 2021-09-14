from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash, jsonify
from flask_login import login_required, current_user
from pm.forms.biz.program import ProgramForm, ProgramSearchForm, ProgramMemberForm, ProgramStatusForm
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
    selected_ids = []        # 已选人员ID(用于过滤可选成员)
    selected = []            # 已选人员(用于列表显示)
    form.pro_roles.data = enum_id
    for pro_member in pro_members:
        # 添加所有已添加人员，用于过滤可选人员
        selected_ids.append(pro_member.member.id)
        # 添加当前项目角色的已选人员
        if pro_member.pro_role_id == enum_id:
            selected.append((pro_member.member.id, pro_member.member.user_name))
    form.selected.choices = selected
    # 可选成员
    all_users = SysUser.query.all()
    for_select = []
    #print('Select id : ', selected_ids)
    #print('Department id : ', dept_id)
    for user in all_users:
        #print('User id is : ', user.user_id, ', department id : ' , user.dept_id)
        if user.user_id != 'admin' and user.id not in selected_ids and user.dept_id == dept_id: # 除去管理员及已添加到项目的人员之后当前部门下的人员
            for_select.append((user.id, user.user_name))
    form.for_select.choices = for_select
    return render_template('biz/program/members.html', form=form, program=program)
@bp_pro.route('/current_members/<pro_id>/<dept_id>/<role_id>', methods=['POST'])
@login_required
@log_record('获取当前项目成员')
def current_members(pro_id, dept_id, role_id):
    program = BizProgram.query.get_or_404(pro_id)
    # 已选成员
    pro_members = program.members
    selected_ids = []   # 已选人员ID(用于过滤可选成员)
    selected = []       # 已选人员(用于列表显示)
    for pro_member in pro_members:
        # 添加所有已添加人员，用于过滤可选人员
        selected_ids.append(pro_member.member.id)
        # 添加当前项目角色的已选人员
        if pro_member.pro_role_id == role_id:
            selected.append((pro_member.member.id, pro_member.member.user_name))
    # 可选成员
    all_users = SysUser.query.all()
    for_select = []
    for user in all_users:
        if user.user_id != 'admin' and user.id not in selected_ids and user.dept_id == dept_id: # 除去管理员及已添加到项目的人员之后当前部门下的人员
            for_select.append((user.id, user.user_name))
    return jsonify(selected=selected, for_select=for_select)
@bp_pro.route('/add_members', methods=['POST'])
@login_required
@log_record('保存项目成员')
def add_members():
    data = request.get_json()
    pro_id = data['pro_id']
    role_id = data['role_id']
    selected = data['selected']
    '''
    print('Program id : ', pro_id)
    print('Role id : ', role_id)
    print('Selected : ', selected)
    '''
    # 解除对应角色的人员关联信息并删除对应的人员
    program = BizProgram.query.get_or_404(pro_id)
    for pro_member in program.members:
        if pro_member.pro_role_id == role_id:
            # 解除关联
            program.members.remove(pro_member)
            db.session.commit()
            # 删除成员
            db.session.delete(pro_member)
            db.session.commit()
    # 添加当前选择的用户
    new_members = selected.split(',')
    for member_id in new_members:
        print('New member id : ', member_id)
        new_member = BizProgramMember(
            id=uuid.uuid4().hex,
            pro_role_id=role_id,
            member_id=member_id,
            operator_id=current_user.id
        )
        db.session.add(new_member)
        db.session.commit()
        # 创建关联
        program.members.append(new_member)
    # 提交保存关联
    db.session.commit()
    return jsonify(code=1, message='添加成功!')
@bp_pro.route('/status/<pro_id>', methods=['GET', 'POST'])
@login_required
@log_record('维护项目状态')
def status(pro_id):
    program = BizProgram.query.get_or_404(pro_id)
    form = ProgramStatusForm()
    form.pro_id.data = pro_id
    if form.validate_on_submit():
        flash('状态维护完成！')
        return redirect(url_for('.status', pro_id=form.pro_id.data))
    return render_template('biz/program/status.html', form=form, program=program)