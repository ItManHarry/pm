import multiprocessing

from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, current_user
from pm.forms.auth import LoginForm
from pm.plugins import db
from pm.models import SysUser, SysLog, SysMenu
from pm.utils import redirect_back
import uuid, jpype
bp_auth = Blueprint('auth', __name__)
@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    '''
    系统登录
    :return:
    '''
    #if current_user.is_authenticated:
        #return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        user_pwd = form.user_pwd.data
        print('User id is %s, password is %s' %(user_id, user_pwd))
        user = SysUser.query.filter_by(user_id=user_id.lower()).first()
        if user:
            if user.status:
                if user.is_ad:
                    # AD验证
                    jvm_path = current_app.config['JVM_PATH']
                    ad_jar_path = current_app.config['AD_JAR_PATH'] + '\\ad.auth.module-1.0.jar'
                    # 如果已启动，捕捉异常后跳过启动JVM
                    try:
                        jpype.startJVM(jvm_path, '-ea', '-Djava.class.path=' + ad_jar_path)
                    except:
                        pass
                    jpype.java.lang.System.out.println('Hello world from JAVA!!!')
                    package = jpype.JPackage('DSGAuthPkg')
                    auth = package.Auth("authsj.corp.doosan.com", "dsg\\" + user_id, user_pwd)
                    validate_ok = auth.validateUser(user_id, user_pwd)
                else:
                    validate_ok = user.validate_password(user_pwd)
                if validate_ok:
                    login_user(user, True)
                    log = SysLog(id=uuid.uuid4().hex, url='auth.login', operation='Login into system', user=user, operator_id=user.id)
                    db.session.add(log)
                    db.session.commit()
                    # 获取系统分配的模块权限
                    menus = user.role.menus
                    menu_ids = []
                    for menu in menus:
                        menu_ids.append(menu.id)
                    #print('All authed menu ids : >>>>>>>>>>>>>>>>>>>> ', menu_ids)
                    # 按照模块别进行排序
                    authed_menus = SysMenu.query.filter(SysMenu.id.in_(menu_ids)).order_by(SysMenu.module_id.desc()).all()
                    #print('Authed menus order by module id >>>>>', authed_menus)
                    tmp = []
                    modules = []
                    for menu in authed_menus:
                        module = menu.module
                        if module not in tmp:
                            tmp.append(module)
                            modules.append((module.default_url, module.id, module.name, module.code))
                    session['modules'] = modules
                    print('Modules : ', session.get('modules'))
                    return redirect_back()
                else:
                    flash('密码错误！')
            else:
                flash('用户已停用！')
            '''
                if user.is_ad:
                    jpype.shutdownJVM()
            '''
        else:
            flash('用户不存在！')
    return render_template('auth/sign_in.html', form=form)
@bp_auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('.login'))