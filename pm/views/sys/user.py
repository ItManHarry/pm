'''
系统用户信息管理
'''
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from pm.decorators import log_record
from pm.plugins import db
from pm.models import SysUser, SysRole, BizDept
from pm.forms.sys.user import UserForm, UserSearchForm
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
    form = UserForm()
    roles = []
    depts = []
    for role in SysRole.query.order_by(SysRole.name).all():
        roles.append((role.id, role.name))
    form.role.choices = roles
    for dept in BizDept.query.order_by(BizDept.code).all():
        depts.append((dept.id, dept.name))
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