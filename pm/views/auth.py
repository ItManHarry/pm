from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from pm.forms.auth import LoginForm
from pm.plugins import db
from pm.models import SysUser, SysLog
from pm.utils import redirect_back
bp_auth = Blueprint('auth', __name__)
@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    '''
    系统登录
    :return:
    '''
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        user_pwd = form.user_pwd.data
        user = SysUser.query.filter_by(user_id=user_id.lower()).first()
        if user:
            if user.validate_password(user_pwd):
                login_user(user, True)
                log = SysLog(url='auth.login', operation='Login into system', user=user, operator_id=user.id)
                db.session.add(log)
                db.session.commit()
                return redirect_back()
            else:
                flash('密码错误！')
        else:
            flash('用户不存在！')
    return render_template('auth/login.html', form=form)
@bp_auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('.login'))