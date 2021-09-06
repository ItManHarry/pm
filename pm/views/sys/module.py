'''
系统模块管理
'''
import uuid
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from pm.forms.sys.module import ModuleSearchForm, ModuleForm
from pm.models import SysModule
from pm.decorators import log_record
from pm.plugins import db
bp_module = Blueprint('module', __name__)
@bp_module.route('/index', methods=['GET', 'POST'])
@login_required
@log_record('查询系统模块清单')
def index():
    name = ''
    form = ModuleSearchForm()
    if request.method == 'POST':
        name = form.name.data
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    pagination = SysModule.query.filter(SysModule.name.like('%' + name + '%')).order_by(SysModule.name.desc()).paginate(page, per_page)
    modules = pagination.items
    return render_template('sys/module/index.html', form=form, pagination=pagination, modules=modules)
@bp_module.route('/add', methods=['GET', 'POST'])
@login_required
@log_record('新增系统模块')
def add():
    form = ModuleForm()
    if form.validate_on_submit():
        module = SysModule(
            id=uuid.uuid4().hex,
            code = form.code.data,
            name=form.name.data,
            default_url=form.default_url.data,
            operator_id=current_user.id)
        db.session.add(module)
        db.session.commit()
        flash('模块添加成功！')
    return render_template('sys/module/add.html', form=form)
@bp_module.route('/eidt/<id>', methods=['GET', 'POST'])
@login_required
@log_record('修改系统模块')
def edit(id):
    form = ModuleForm()
    module = SysModule.query.get_or_404(id)
    if request.method == 'GET':
        form.name.data = module.name
        form.code.data = module.code
        form.id.data = module.id
        form.default_url.data = module.default_url
    if form.validate_on_submit():
        module.name = form.name.data
        module.code = form.code.data
        module.default_url = form.default_url.data
        module.operator_id = current_user.id
        db.session.commit()
        flash('模块修改成功！')
        return redirect(url_for('.edit', id=module.id))
    return render_template('sys/module/edit.html', form=form)
@bp_module.route('/menus/<id>', methods=['POST'])
@login_required
@log_record('查看模块下的菜单')
def menus(id):
    module = SysModule.query.get_or_404(id)
    ms = []
    for menu in module.menus:
        ms.append(menu.name)
    return jsonify(menus=ms)