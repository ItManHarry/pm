from flask import Blueprint, session, redirect, url_for
from flask_login import login_required, current_user
from pm.models import SysModule, SysMenu
bp_sys = Blueprint('sys', __name__)
@bp_sys.route('/index/<module_id>')
@login_required
def index(module_id):
    # 获取当前模块
    module = SysModule.query.get_or_404(module_id)
    session['nav'] = module.code                # 对应模块表中的code
    session['module_id'] = module_id            # 每个页面的链接跳转参数
    # 已授权菜单
    role = current_user.role
    menu_ids = []
    for menu in role.menus:
        menu_ids.append(menu.id)
    # 排序
    authed_menus = SysMenu.query.filter(SysMenu.id.in_(menu_ids)).order_by(SysMenu.module_id, SysMenu.name).all()
    menus = []
    for menu in authed_menus:
        if menu.module_id == module.id:
            menus.append((menu.url, menu.icon, menu.name))
    print('menus are : ', menus)
    session['menus'] = menus
    return redirect(url_for(module.default_url, module_id=module_id))