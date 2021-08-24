from flask import Flask
import click
from pm.configs import configurations
from pm.plugins import db, bootstrap, moment, ckeditor, migrate, csrf, dropzone
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
def register_webapp_global_path(app):
    @app.route('/')
    def index():
        return '<h1>Program Management</h1>'
def register_webapp_global_context(app):
    from pm.utils import get_time, format_time
    @app.context_processor
    def config_template_context():
        return dict(get_time=get_time, format_time=format_time)
def register_webapp_errors(app):
    pass
def register_webapp_views(app):
    pass
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
            #创建人员/更新人员信息
            timestamp_utc = datetime.utcnow()
            timestamp_loc = datetime.now()
            creator = SysUserCreator(creator_id=user.id, timestamp_utc=timestamp_utc, timestamp_loc=timestamp_loc)
            updater = SysUserUpdater(updater_id=user.id, timestamp_utc=timestamp_utc, timestamp_loc=timestamp_loc)
            db.session.add(creator)
            db.session.add(updater)
            db.session.commit()
        click.echo('管理员创建成功')
        click.echo('系统初始化完成')