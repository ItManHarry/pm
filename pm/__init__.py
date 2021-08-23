from flask import Flask
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
    pass