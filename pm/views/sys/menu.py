'''
系统菜单管理
'''
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, jsonify, session
from flask_login import login_required, current_user
from pm.models import SysMenu, SysModule
from pm.plugins import db
from pm.decorators import log_record
from pm.forms.sys.menu import MenuForm, MenuSearchForm
import uuid
bp_menu = Blueprint('menu', __name__)
@bp_menu.route('/index', methods=['GET', 'POST'])
@login_required
@log_record('查看系统菜单清单')
def index():
    form = MenuSearchForm()
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        try:
            name = session['menu_view_search_name'] if session['menu_view_search_name'] else ''  # 菜单名称
        except KeyError:
            name = ''
        form.name.data = name
    if request.method == 'POST':
        page = 1
        name = form.name.data
        session['menu_view_search_name'] = name
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    pagination = SysMenu.query.filter(SysMenu.name.like('%'+name+'%')).order_by(SysMenu.module_id, SysMenu.name).paginate(page, per_page)
    menus = pagination.items
    return render_template('sys/menu/index.html', form=form, pagination=pagination, menus=menus)
@bp_menu.route('/add', methods=['GET', 'POST'])
@login_required
@log_record('新增系统菜单')
def add():
    form = MenuForm()
    form.module.choices = get_modules()
    if form.validate_on_submit():
        menu = SysMenu(
            id=uuid.uuid4().hex,
            name=form.name.data,
            url=form.url.data,
            desc=form.desc.data,
            module_id=form.module.data,
            icon=form.icon.data,
            operator_id=current_user.id
        )
        db.session.add(menu)
        db.session.commit()
        flash('新增菜单成功！')
        return redirect(url_for('.add'))
    return render_template('sys/menu/add.html', form=form)

@bp_menu.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
@log_record('修改系统菜单')
def edit(id):
    form = MenuForm()
    menu = SysMenu.query.get_or_404(id)
    form.module.choices = get_modules()
    if request.method == 'GET':
        form.id.data = menu.id
        form.name.data = menu.name
        form.url.data = menu.url
        form.desc.data = menu.desc
        form.icon.data = menu.icon
        form.module.data = menu.module_id
    if form.validate_on_submit():
        menu.name = form.name.data
        menu.url = form.url.data
        menu.desc = form.desc.data
        menu.icon = form.icon.data
        menu.module_id = form.module.data
        menu.operator_id = current_user.id
        db.session.commit()
        flash('菜单修改成功！')
        return redirect(url_for('.edit', id=form.id.data))
    return render_template('sys/menu/edit.html', form=form)
@bp_menu.route('/status/<id>/<int:status>', methods=['POST'])
@login_required
@log_record('启用/停用系统菜单')
def status(id, status):
    menu = SysMenu.query.get_or_404(id)
    menu.status = True if status == 1 else False
    menu.operator_id = current_user.id
    db.session.commit()
    return jsonify(code=1, message='菜单状态修改成功！')
def get_modules():
    modules = []
    for module in SysModule.query.order_by(SysModule.name.desc()).all():
        modules.append((module.id, module.name))
    return modules