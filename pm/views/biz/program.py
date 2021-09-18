from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash, jsonify
from flask_login import login_required, current_user
from pm.forms.biz.program import ProgramForm, ProgramSearchForm, ProgramMemberForm, ProgramStatusForm, ProgramInvoiceForm
from pm.models import BizProgram, SysUser, BizProgramMember, BizDept, BizProgramStatus, BizProgramInvoice
from pm.plugins import db
from pm.decorators import log_record
from pm.utils import get_date, get_options
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
    pro_roles = get_options('D002')
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
    status = program.status
    form = ProgramStatusForm()
    form.pro_id.data = pro_id
    # 获取下拉列表值
    form.clazz_id.choices = get_options('D004')
    form.state_id.choices = get_options('D003')
    # GET请求下如果已经有状态信息的话进行form赋值
    if request.method == 'GET' and status:
        form.enterprise.data = status.enterprise
        form.client.data = status.client
        form.client_dept.data = status.client_dept
        form.charge_dept.data = status.charge_dept
        form.new.data = status.new
        form.clazz_id.data = status.clazz_id
        form.state_id.data = status.state_id
        form.odds.data = status.odds
        form.con_start.data = status.con_start
        form.con_end.data = status.con_end
        form.process_now.data = status.process_now
        form.budget.data = status.budget
    if form.validate_on_submit():
        if status:  # 执行修改
            status.enterprise = form.enterprise.data
            status.client = form.client.data
            status.client_dept = form.client_dept.data
            status.charge_dept = form.charge_dept.data
            status.new = form.new.data
            status.clazz_id = form.clazz_id.data
            status.state_id = form.state_id.data
            status.odds = form.odds.data
            status.con_start = form.con_start.data
            status.con_end = form.con_end.data
            status.process_now = form.process_now.data
            status.budget = form.budget.data
            status.operator_id = current_user.id
            db.session.commit()
        else:   # 执行新增
            status = BizProgramStatus(
                id=uuid.uuid4().hex,
                program=program,
                enterprise=form.enterprise.data,
                client=form.client.data,
                client_dept=form.client_dept.data,
                charge_dept=form.charge_dept.data,
                new=form.new.data,
                clazz_id=form.clazz_id.data,
                state_id=form.state_id.data,
                odds=form.odds.data,
                con_start=form.con_start.data,
                con_end=form.con_end.data,
                process_now=form.process_now.data,
                budget=form.budget.data,
                operator_id=current_user.id
            )
            db.session.add(status)
            db.session.commit()
        flash('项目状态维护完成！')
        return redirect(url_for('.status', pro_id=form.pro_id.data))
    return render_template('biz/program/status.html', form=form, program=program)
@bp_pro.route('/invoices/<pro_id>')
@login_required
@log_record('管理项目开票信息')
def invoices(pro_id):
    program = BizProgram.query.get_or_404(pro_id)
    invoices = program.invoices
    return render_template('biz/program/invoices/index.html', invoices=invoices, program=program)
@bp_pro.route('/invoices/add_invoice/<pro_id>', methods=['GET', 'POST'])
@login_required
@log_record('新增项目发票信息')
def add_invoice(pro_id):
    program = BizProgram.query.get_or_404(pro_id)
    form = ProgramInvoiceForm()
    form.pro_id.data = pro_id
    form.category_id.choices = get_options('D005')
    if form.validate_on_submit():
        invoice = BizProgramInvoice(
            id=uuid.uuid4().hex,
            program=program,
            category_id=form.category_id.data,
            percent=form.percent.data,
            make_out=form.make_out.data,
            make_out_dt=form.make_out_dt.data,
            delivery_dt=form.delivery_dt.data,
            remark=form.remark.data,
            operator_id=current_user.id
        )
        db.session.add(invoice)
        db.session.commit()
        flash('发票信息新增成功！')
        return redirect(url_for('.add_invoice', pro_id=form.pro_id.data))
    return render_template('biz/program/invoices/add.html', form=form, program=program)
@bp_pro.route('/invoices/edit_invoice/<pro_id>/<invoice_id>', methods=['GET', 'POST'])
@login_required
@log_record('修改项目发票信息')
def edit_invoice(pro_id, invoice_id):
    program = BizProgram.query.get_or_404(pro_id)
    form = ProgramInvoiceForm()
    form.pro_id.data = pro_id
    form.invoice_id.data = invoice_id
    form.category_id.choices = get_options('D005')
    invoice = BizProgramInvoice.query.get_or_404(invoice_id)
    if request.method == 'GET':
        form.category_id.data = invoice.category_id
        form.percent.data = invoice.percent
        form.make_out.data = invoice.make_out
        form.make_out_dt.data = invoice.make_out_dt
        form.delivery_dt.data = invoice.delivery_dt
        form.remark.data = invoice.remark
    if form.validate_on_submit():
        invoice.category_id = form.category_id.data
        invoice.percent = form.percent.data
        invoice.make_out = form.make_out.data
        invoice.make_out_dt = form.make_out_dt.data
        invoice.delivery_dt = form.delivery_dt.data
        invoice.remark = form.remark.data
        invoice.operator_id = current_user.id
        db.session.commit()
        flash('发票信息更改成功！')
        return redirect(url_for('.edit_invoice', pro_id=pro_id, invoice_id=invoice_id))
    return render_template('biz/program/invoices/edit.html', form=form, program=program)