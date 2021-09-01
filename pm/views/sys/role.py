'''
系统角色管理
'''
import uuid
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from pm.forms.sys.role import RoleSearchForm, RoleForm
from pm.models import SysRole
from pm.decorators import log_record
from pm.plugins import db
bp_role = Blueprint('role', __name__)
@bp_role.route('/index', methods=['GET', 'POST'])
@login_required
@log_record('查询系统角色清单')
def index():
    name = ''
    form = RoleSearchForm()
    if request.method == 'POST':
        name = form.name.data
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    pagination = SysRole.query.filter(SysRole.name.like('%' + name + '%')).order_by(SysRole.name.desc()).paginate(page, per_page)
    roles = pagination.items
    return render_template('sys/role/index.html', form=form, pagination=pagination, roles=roles)
@bp_role.route('/add', methods=['GET', 'POST'])
@login_required
@log_record('新增系统角色')
def add():
    form = RoleForm()
    if form.validate_on_submit():
        role = SysRole(id=uuid.uuid4().hex, name=form.name.data, operator_id=current_user.id)
        db.session.add(role)
        db.session.commit()
        flash('角色添加成功！')
        return redirect(url_for('.add'))
    return render_template('sys/role/add.html', form=form)
@bp_role.route('/eidt/<id>', methods=['GET', 'POST'])
@login_required
@log_record('修改系统角色')
def edit(id):
    form = RoleForm()
    role = SysRole.query.get_or_404(id)
    if request.method == 'GET':
        form.name.data = role.name
        form.id.data = role.id
    if form.validate_on_submit():
        role.name = form.name.data
        role.operator_id = current_user.id
        db.session.commit()
        flash('角色修改成功！')
        return redirect(url_for('.edit', id=role.id))
    return render_template('sys/role/edit.html', form=form)