from flask import Flask, redirect, url_for, render_template
from flask_wtf.csrf import CSRFError
import click
from pm.configs import configurations
from pm.plugins import db, bootstrap, moment, ckeditor, migrate, csrf, dropzone, login_manager
def create_app(config=None):
    if config == None:
        config = 'dev_config'
    app = Flask('pm')
    app.config.from_object(configurations[config])
    register_webapp_plugins(app)
    register_webapp_global_path(app)
    register_webapp_global_context(app)
    register_webapp_errors(app)
    register_webapp_views(app)
    register_webapp_shell(app)
    register_webapp_commands(app)
    return app
def register_webapp_plugins(app):
    db.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    ckeditor.init_app(app)
    migrate.init_app(app)
    csrf.init_app(app)
    dropzone.init_app(app)
    login_manager.init_app(app)
def register_webapp_global_path(app):
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    @app.before_request
    def request_intercept():
        pass
def register_webapp_global_context(app):
    from pm.utils import get_time, format_time
    @app.context_processor
    def config_template_context():
        return dict(get_time=get_time, format_time=format_time)
def register_webapp_errors(app):
    @app.errorhandler(400)
    def request_invalid(e):
        return render_template('errors/400.html'), 400
    @app.errorhandler(403)
    def request_invalid(e):
        return render_template('errors/403.html'), 403
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    @app.errorhandler(500)
    def inner_error(e):
        return render_template('errors/500.html'), 500
    @app.errorhandler(CSRFError)
    def csrf_error(e):
        return render_template('errors/csrf.html')
def register_webapp_views(app):
    from pm.views.auth import bp_auth
    from pm.views.main import bp_main
    from pm.views.system import bp_sys
    from pm.views.sys.user import bp_user
    from pm.views.sys.org import bp_org
    app.register_blueprint(bp_auth, url_prefix='/auth')
    app.register_blueprint(bp_main, url_prefix='/main')
    app.register_blueprint(bp_sys,  url_prefix='/sys')
    app.register_blueprint(bp_user, url_prefix='/user')
    app.register_blueprint(bp_org,  url_prefix='/org')
def register_webapp_shell(app):
    @app.shell_context_processor
    def config_shell_context():
        return dict(db=db)
def register_webapp_commands(app):
    @app.cli.command()
    @click.option('--admin_code', prompt=True, help='管理员账号')
    @click.option('--admin_password', prompt=True, help='管理员密码', hide_input=True, confirmation_prompt=True)
    def init(admin_code, admin_password):
        from pm.models import SysUser, SysUserCreator, SysUserUpdater, SysRole
        from datetime import datetime
        click.echo('执行数据库初始化...')
        db.create_all()
        click.echo('数据库初始化完毕')
        click.echo('创建管理员角色')
        role = SysRole(name='Administrator')
        db.session.add(role)
        db.session.commit()
        click.echo('创建管理员')
        user = SysUser.query.first()
        if user:
            click.echo('管理员已存在，跳过创建。')
        else:
            click.echo('执行创建管理员')
            user = SysUser(
                user_id=admin_code.lower(),
                user_name='Administrator',
                svn_id='',
                svn_pwd='',
                role_id=role.id
            )
            user.set_password(admin_password)
            db.session.add(user)
            db.session.commit()
            '''
                设置创建人员/更新人员信息
                注：此处设置了创建人员和更新人员仅仅为了测试，正常情况只设置创建人员即可
            '''
            user.set_created_by(user)
            user.set_updated_by(user)
        click.echo('管理员创建成功')
        click.echo('系统初始化完成')