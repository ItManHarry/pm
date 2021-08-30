'''
系统角色管理
'''
from flask import Blueprint, render_template, request, current_app
from flask_login import login_required
from pm.forms.sys.role import RoleSearchForm
from pm.models import SysRole
from pm.decorators import log_record
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
    return render_template('sys/role/add.html')
@bp_role.route('/eidt/<id>', methods=['GET', 'POST'])
@login_required
@log_record('修改系统角色')
def edit(id):
    return render_template('sys/role/edit.html')