'''
系统菜单管理
'''
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
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
    name = ''
    if request.method == 'POST':
        name = form.name.data
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    pagination = SysMenu.query.filter(SysMenu.name.like('%'+name+'%')).order_by(SysMenu.name).paginate(page, per_page)
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
    return 'Edit Menu'
def get_modules():
    modules = []
    for module in SysModule.query.order_by(SysModule.name.desc()).all():
        modules.append((module.id, module.name))
    return modules