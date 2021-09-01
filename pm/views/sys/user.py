'''
系统用户信息管理
'''
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, jsonify
from flask_login import login_required, current_user
from pm.decorators import log_record
from pm.plugins import db
from pm.models import SysUser, SysRole, BizDept
from pm.forms.sys.user import UserSearchForm, AddUserForm, EditUserForm
import uuid
bp_user = Blueprint('user', __name__)
@bp_user.route('/index', methods=['GET', 'POST'])
@login_required
@log_record('查看用户清单')
def index():
    code = ''
    name = ''
    form = UserSearchForm()
    if request.method == 'POST':
        code = form.code.data
        name = form.name.data
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    pagination = SysUser.query.filter(SysUser.user_id.like('%'+code+'%'), SysUser.user_name.like('%'+name+'%')).order_by(SysUser.user_name).paginate(page, per_page)
    users = pagination.items
    return render_template('sys/users/index.html', form=form, pagination=pagination, users=users)
@bp_user.route('/add', methods=['GET', 'POST'])
@login_required
@log_record('新增用户')
def add():
    form = AddUserForm()
    roles, depts = get_user_selects()
    form.role.choices = roles
    form.dept.choices = depts
    if form.validate_on_submit():
        user = SysUser(
            id=uuid.uuid4().hex,
            user_id=form.code.data.lower(),
            user_name=form.name.data,
            email=form.email.data.lower(),
            svn_id=form.svn_id.data,
            svn_pwd=form.svn_pwd.data,
            role_id=form.role.data,
            dept_id=form.dept.data,
            operator_id=current_user.id
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        user.set_created_by(current_user)
        flash('用户添加成功！')
        return redirect(url_for('.add'))
    return render_template('sys/users/add.html', form=form)
#获取角色/部门下拉清单
def get_user_selects():
    roles = []
    depts = []
    for role in SysRole.query.order_by(SysRole.name).all():
        roles.append((role.id, role.name))
    for dept in BizDept.query.order_by(BizDept.code).all():
        depts.append((dept.id, dept.name))
    return roles, depts
@bp_user.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
@log_record('编辑用户')
def edit(id):
    form = EditUserForm()
    user = SysUser.query.get_or_404(id)
    roles, depts = get_user_selects()
    form.role.choices = roles
    form.dept.choices = depts
    if request.method == 'GET':
        form.id.data = user.id
        form.code.data = user.user_id
        form.name.data = user.user_name
        form.dept.data = user.dept_id
        form.role.data = user.role_id
        form.email.data = user.email
        form.svn_id.data = user.svn_id
        form.svn_pwd.data = user.svn_pwd
    if form.validate_on_submit():
        user.user_id = form.code.data.lower()
        user.user_name = form.name.data
        user.email = form.email.data.lower()
        if form.svn_id is not None and form.svn_id != '':
            user.svn_id = form.svn_id.data
        if form.svn_pwd is not None and form.svn_pwd != '':
            user.svn_pwd = form.svn_pwd.data
        user.role_id = form.role.data
        user.dept_id = form.dept.data
        user.operator_id = current_user.id
        db.session.commit()
        user.set_updated_by(current_user)
        flash('用户修改成功！')
        return redirect(url_for('.edit', id=form.id.data))
    return render_template('sys/users/edit.html', form=form)
@bp_user.route('/status/<id>/<int:status>', methods=['POST'])
@log_record('更改用户状态')
def status(id, status):
    user = SysUser.query.get_or_404(id)
    user.status = True if status == 1 else False
    user.operator_id = current_user.id
    db.session.commit()
    user.set_updated_by(current_user)
    return jsonify(code=1, message='状态更新成功!')
@bp_user.route('/reset_password/<id>', methods=['POST'])
@log_record('重置密码')
def reset_password(id):
    user = SysUser.query.get_or_404(id)
    user.set_password('Pm12345678')
    user.operator_id = current_user.id
    db.session.commit()
    user.set_updated_by(current_user)
    return jsonify(code=1, message='密码重置成功！')