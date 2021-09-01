'''
系统部门信息管理
'''
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from pm.models import BizDept
from pm.plugins import db
from pm.forms.sys.org import OrgSearchForm, OrgForm
from pm.decorators import log_record
import uuid
bp_org = Blueprint('org', __name__)

@bp_org.route('/index', methods=['GET', 'POST'])
@login_required
@log_record('查询部门清单')
def index():
    code = ''
    name = ''
    form = OrgSearchForm()
    if request.method == 'POST':
        code = form.code.data
        name = form.name.data
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    pagination = BizDept.query.filter(BizDept.code.like('%'+code+'%'), BizDept.name.like('%'+name+'%')).order_by(BizDept.code).paginate(page, per_page)
    departments = pagination.items
    return render_template('sys/org/index.html', pagination=pagination, departments=departments, form=form)

@bp_org.route('/add', methods=['GET', 'POST'])
@login_required
@log_record('新增部门信息')
def add():
    form = OrgForm()
    departments = BizDept.query.order_by(BizDept.code).all()
    department_list = []
    for department in departments:
        department_list.append((department.id, department.name))
    form.parent.choices = department_list
    if form.validate_on_submit():
        department = BizDept(id=uuid.uuid4().hex, code=form.code.data.lower(), name=form.name.data, operator_id=current_user.id)
        db.session.add(department)
        db.session.commit()
        has_parent = form.has_parent.data
        if has_parent and form.parent.data is not None:
            department.set_parent_dept(BizDept.query.get(form.parent.data))
        flash('部门信息添加成功！')
        return redirect(url_for('.add'))
    return render_template('sys/org/add.html', form=form)
@bp_org.route('/eidt/<id>', methods=['GET', 'POST'])
@login_required
@log_record('修改部门信息')
def edit(id):
    form = OrgForm()
    edit_department = BizDept.query.get_or_404(id)
    '''
        设置上级部门下拉列表
        注:上级部门下拉列表需剔除当前部门及子部门
    '''
    self_and_children = [edit_department.id]
    get_child_dept(edit_department, self_and_children)  # 递归获取子部门及子子部门
    print('Self and child department ids : ', self_and_children)
    departments = BizDept.query.order_by(BizDept.code).all()
    department_list = []
    for department in departments:
        if department.id not in self_and_children:
            department_list.append((department.id, department.name))
    form.parent.choices = department_list
    if request.method == 'GET':
        form.id.data = edit_department.id
        form.code.data = edit_department.code
        form.name.data = edit_department.name
        form.parent.data = edit_department.my_parent_dept.id if edit_department.my_parent_dept else ''
    if form.validate_on_submit():
        edit_department.code = form.code.data
        edit_department.name = form.name.data
        edit_department.operator_id = current_user.id
        db.session.commit()
        has_parent = form.has_parent.data
        if has_parent and form.parent.data is not None:
            edit_department.set_parent_dept(BizDept.query.get(form.parent.data))
        else:
            print('不执行上级部门更新')
        flash('部门信息更新成功！')
        return redirect(url_for('.edit', id=form.id.data))
    return render_template('sys/org/edit.html', form=form)
#递归获取子部门(多级部门)
def get_child_dept(parent, children):
    child_departments = parent.my_child_dept
    if child_departments:
        for child in child_departments:
            children.append(child.child_dept_id)
            get_child_dept(BizDept.query.get(child.child_dept_id), children)
    else:
        return children
@bp_org.route('/status/<id>/<int:status>', methods=['POST'])
@log_record('更改部门状态')
def status(id, status):
    department = BizDept.query.get_or_404(id)
    department.status = True if status == 1 else False
    department.operator_id = current_user.id
    db.session.commit()
    return jsonify(code=1, message='状态更新成功!')