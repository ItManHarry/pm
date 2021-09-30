from flask import Flask, redirect, url_for, render_template
from flask_wtf.csrf import CSRFError
import click, uuid
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
    from pm.utils import get_time, format_time, get_current_user
    @app.context_processor
    def config_template_context():
        return dict(get_time=get_time, format_time=format_time, get_current_user=get_current_user)
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
    from pm.views.sys.role import bp_role
    from pm.views.sys.module import bp_module
    from pm.views.sys.menu import bp_menu
    from pm.views.sys.dicts import bp_dict
    from pm.views.biz.program import bp_pro
    from pm.views.biz.issue import bp_issue
    from pm.views.biz.report import bp_report
    app.register_blueprint(bp_auth, url_prefix='/auth')
    app.register_blueprint(bp_main, url_prefix='/main')
    app.register_blueprint(bp_sys,  url_prefix='/sys')
    app.register_blueprint(bp_user, url_prefix='/user')
    app.register_blueprint(bp_org,  url_prefix='/org')
    app.register_blueprint(bp_role, url_prefix='/role')
    app.register_blueprint(bp_module, url_prefix='/module')
    app.register_blueprint(bp_menu, url_prefix='/menu')
    app.register_blueprint(bp_dict, url_prefix='/dict')
    app.register_blueprint(bp_pro, url_prefix='/pro')
    app.register_blueprint(bp_issue, url_prefix='/iss')
    app.register_blueprint(bp_report, url_prefix='/rpt')
def register_webapp_shell(app):
    @app.shell_context_processor
    def config_shell_context():
        return dict(db=db)
def register_webapp_commands(app):
    @app.cli.command()
    @click.option('--admin_code', prompt=True, help='管理员账号')
    @click.option('--admin_password', prompt=True, help='管理员密码', hide_input=True, confirmation_prompt=True)
    def init(admin_code, admin_password):
        from pm.models import SysUser, SysUserCreator, SysUserUpdater, SysRole, SysModule, SysMenu, SysDict, SysEnum
        click.echo('执行数据库初始化...')
        db.create_all()
        click.echo('数据库初始化完毕')
        click.echo('创建管理员角色')
        role = SysRole.query.first()
        if role:
            click.echo('管理员角色已存在，跳过创建')
        else:
            role = SysRole(id=uuid.uuid4().hex, name='Administrator')
            db.session.add(role)
            db.session.commit()
        click.echo('创建管理员')
        user = SysUser.query.first()
        if user:
            click.echo('管理员已存在，跳过创建')
        else:
            click.echo('执行创建管理员')
            user = SysUser(
                id=uuid.uuid4().hex,
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
        click.echo('初始化系统模块')
        modules = SysModule.query.all()
        if modules:
            click.echo('系统模块已创建，跳过')
        else:
            modules = [
                ('pro', '项目管理', 'pro.index'),
                ('iss', 'ISSUE管理', 'iss.index'),
                ('org', '人事组织', 'user.index'),
                ('sys', '系统管理', 'dict.index')
            ]
            for module_info in modules:
                module = SysModule(
                    id=uuid.uuid4().hex,
                    code=module_info[0],
                    name=module_info[1],
                    default_url=module_info[2],
                    operator_id=user.id
                )
                db.session.add(module)
                db.session.commit()
        click.echo('系统模块初始化完成')
        click.echo('初始化系统菜单')
        # 菜单名称, URL地址, 菜单描述, 菜单图标, 模块所属
        menus = [
            ('字典管理', 'dict.index', '管理系统下拉选项，包括新增、修改等', 'fas fa-book', 'sys'),
            ('模块管理', 'module.index', '管理系统模块(新增/修改等)', 'fas fa-project-diagram', 'sys'),
            ('菜单管理', 'menu.index', '管理系统菜单(新增/修改/停用等)', 'fas fa-list', 'sys'),
            ('角色管理', 'role.index', '管理系统角色(新增/修改等)', 'fas fa-gavel', 'sys'),
            ('用户管理', 'user.index', '管理系统用户(添加、修改、启用/停用等)', 'fas fa-users', 'org'),
            ('组织管理', 'org.index', '管理部门组织信息(新增/修改/停用等)', 'fas fa-sitemap', 'org'),
            ('ISSUE事项', 'iss.index', '当前用户管理所属项目的ISSUE信息', 'fas fa-newspaper', 'iss'),
            ('我的项目', 'pro.index', '当前用户管理自己负责的项目信息', 'fas fa-newspaper', 'pro')
        ]
        if SysMenu.query.all():
            click.echo('系统菜单已创建，跳过')
        else:
            for menu_info in menus:
                menu = SysMenu(
                    id=uuid.uuid4().hex,
                    name=menu_info[0],
                    url=menu_info[1],
                    desc=menu_info[2],
                    icon=menu_info[3],
                    module=SysModule.query.filter_by(code=menu_info[4]).first(),
                    operator_id=user.id
                )
                db.session.add(menu)
                db.session.commit()
                # 设定角色
                role.menus.append(menu)
                db.session.commit()
            click.echo('菜单初始化完成')
        click.echo('初始化系统字典')
        dicts = SysDict.query.all()
        if dicts:
            click.echo('系统字典已创建，跳过')
        else:
            dicts = [
                ('D001', '是否'),
                ('D002', '项目组成员角色'),
                ('D003', '项目状态'),
                ('D004', '项目分类'),
                ('D005', '发票区分'),
                ('D006', 'ISSUE类型'),
                ('D007', 'ISSUE等级'),
                ('D008', 'ISSUE状态')
            ]
            for d in dicts:
                dictionary = SysDict(
                    id=uuid.uuid4().hex,
                    code=d[0],
                    name=d[1],
                    operator_id=user.id
                )
                db.session.add(dictionary)
                db.session.commit()
            click.echo('系统字典初始化完成')
        click.echo('初始化字典枚举值')
        enums = SysEnum.query.all()
        if enums:
            click.echo('字典枚举已维护，跳过')
        else:
            enums = [
                ('1', '是', 'D001'),
                ('2', '否', 'D001'),
                ('1', '开发经理', 'D002'),
                ('2', '开发人员', 'D002'),
                ('3', '业务部门担当', 'D002'),
                ('1', '等待', 'D003'),
                ('2', '合同准备', 'D003'),
                ('3', '起案进行', 'D003'),
                ('4', '进行中', 'D003'),
                ('5', '结束', 'D003'),
                ('1', 'C&SI服务卖出', 'D004'),
                ('2', 'C&SI商品卖出', 'D004'),
                ('1', '首付款', 'D005'),
                ('2', '中期款', 'D005'),
                ('3', '尾款', 'D005'),
                ('1', 'Bug', 'D006'),
                ('2', '改善', 'D006'),
                ('3', 'ISSUE事项', 'D006'),
                ('1', '低', 'D007'),
                ('2', '中', 'D007'),
                ('3', '高', 'D007'),
                ('1', '待确认', 'D008'),
                ('2', '处理中', 'D008'),
                ('3', '处理完成', 'D008'),
                ('4', '已取消', 'D008'),
                ('5', '已关闭', 'D008'),
                ('6', 'Reopen', 'D008')
            ]
            for enum in enums:
                enumeration = SysEnum(
                    id=uuid.uuid4().hex,
                    key=enum[0],
                    display=enum[1],
                    dictionary = SysDict.query.filter_by(code=enum[2]).first(),
                    operator_id=user.id
                )
                db.session.add(enumeration)
                db.session.commit()
            click.echo('字典枚举初始化完成')
        click.echo('系统初始化完成')