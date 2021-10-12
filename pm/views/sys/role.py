'''
系统角色管理
'''
import uuid
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, jsonify, session
from flask_login import login_required, current_user
from pm.forms.sys.role import RoleSearchForm, RoleForm
from pm.models import SysRole, SysMenu
from pm.decorators import log_record
from pm.plugins import db
bp_role = Blueprint('role', __name__)
@bp_role.route('/index', methods=['GET', 'POST'])
@login_required
@log_record('查询系统角色清单')
def index():    
    form = RoleSearchForm()
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        try:
            name = session['role_view_search_name'] if session['role_view_search_name'] else ''  # 角色名称
        except KeyError:
            name = ''
        form.name.data = name
    if request.method == 'POST':
        page = 1
        name = form.name.data
        session['role_view_search_name'] = name
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
@bp_role.route('/menus/<id>', methods=['POST'])
@login_required
def menus(id):
    all_menus = []
    for menu in SysMenu.query.all():
        all_menus.append((menu.id, menu.module.name+' / '+menu.name))
    #print('All menus : ', all_menus)
    role = SysRole.query.get_or_404(id)
    authed_menus = []
    for menu in role.menus:
        authed_menus.append(menu.id)
    print('Authed menus : ', authed_menus)
    return jsonify(all_menus=all_menus, authed_menus=authed_menus)
@bp_role.route('/auth', methods=['POST'])
@login_required
def auth():
    data = request.get_json()
    role_id = data['role_id']
    menu_ids = data['menu_ids']
    print(role_id)
    role = SysRole.query.get_or_404(role_id)
    # 首先移除已授权菜单
    for menu in role.menus:
        role.menus.remove(menu)
        db.session.commit()
    # 添加新授权的菜单
    for menu_id in menu_ids:
        role.menus.append(SysMenu.query.get(menu_id))
    db.session.commit()
    return jsonify(code=1, message='授权成功！')