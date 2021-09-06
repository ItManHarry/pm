from flask import Blueprint, render_template, session
from flask_login import login_required, current_user
from pm.models import SysModule
bp_sys = Blueprint('sys', __name__)
@bp_sys.route('/index/<module_id>')
@login_required
def index(module_id):
    session['nav'] = 'sys'                  # 对应模块表中的code
    session['module_id'] = module_id        # 每个页面的链接跳转参数
    # 获取当前模块
    module = SysModule.query.get_or_404(module_id)
    # 已授权菜单
    role = current_user.role
    authed_menus = role.menus
    menus = []
    for menu in authed_menus:
        if menu.module_id == module.id:
            menus.append(menu)
    return render_template('sys/index.html', menus=menus)