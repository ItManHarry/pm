from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from pm.plugins import db
import uuid
'''
 基础模型
'''
class BaseModel():
    id = db.Column(db.String(32), default=uuid.uuid4().hex, primary_key=True)
    timestamp_utc = db.Column(db.DateTime, default=datetime.utcnow)     #标准时间
    timestamp_loc = db.Column(db.DateTime, default=datetime.now)        #本地时间
'''
    使用模型表建立用户自关联关系
    1. 可以获取创建时间
    2. 对象映射清晰，易于查询
'''
class SysUserCreator(BaseModel, db.Model):
    creator_id = db.Column(db.String(32), db.ForeignKey('sys_user.id'))
    creator = db.relationship('SysUser', foreign_keys=[creator_id], back_populates='creator', lazy='joined')
class SysUserUpdater(BaseModel, db.Model):
    updater_id = db.Column(db.String(32), db.ForeignKey('sys_user.id'))
    updater = db.relationship('SysUser', foreign_keys=[updater_id], back_populates='updater', lazy='joined')
'''
    系统用户表
'''
class SysUser(BaseModel, db.Model, UserMixin):
    user_id = db.Column(db.String(16), unique=True) #用户代码
    user_name = db.Column(db.String(24))            #用户姓名
    user_pwd_hash = db.Column(db.String(128))       #用户密码(加密后)
    svn_id = db.Column(db.String(24))               #svn账号
    svn_pwd = db.Column(db.String(24))              #svn密码
    #created_by = db.relationship('SysUser', secondary=user_creators, primaryjoin=(user_creators.c.creator_id == id), secondaryjoin=(user_creators.c.created_id == id), backref=db.backref('user_creators', lazy='dynamic'))
    #updated_by = db.relationship('SysUser', secondary=user_updaters, primaryjoin=(user_updaters.c.updater_id == id), secondaryjoin=(user_updaters.c.updated_id == id), backref=db.backref('user_updaters', lazy='dynamic'))
    creator = db.relationship('SysUserCreator', foreign_keys=[SysUserCreator.creator_id], back_populates='creator', lazy='dynamic', cascade='all')  #创建者
    updater = db.relationship('SysUserUpdater', foreign_keys=[SysUserUpdater.updater_id], back_populates='updater', lazy='dynamic', cascade='all')  #修改者
    role_id = db.Column(db.String(32), db.ForeignKey('sys_role.id'))    #系统角色ID
    role = db.relationship('SysRole', back_populates='users')           #系统角色
    logs = db.relationship('SysLog', back_populates='user')             #操作日志

    def set_password(self, password):
        self.user_pwd_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.user_pwd_hash, password)
'''
    角色菜单关联表(多对多)
'''
roles_menus = db.Table('roles_menus',
    db.Column('role_id', db.String(32), db.ForeignKey('sys_role.id')),
    db.Column('menu_id', db.String(32), db.ForeignKey('sys_menu.id'))
)
'''
    系统角色
'''
class SysRole(BaseModel, db.Model):
    name = db.Column(db.String(64), unique=True)                #角色名称
    users = db.relationship('SysUser', back_populates='role')   #用户
    menus = db.relationship('SysMenu', secondary='roles_menus', back_populates='roles')
'''
    系统菜单
'''
class SysMenu(BaseModel, db.Model):
    name = db.Column(db.String(64))         #菜单名
    url = db.Column(db.String(24))          #URL地址
    roles = db.relationship('SysRole', secondary='roles_menus', back_populates='menus')
'''
    系统下拉字典表
'''
class SysDict(BaseModel, db.Model):
    code = db.Column(db.String(24), unique=True)    #字典代码
    name = db.Column(db.String(24), unique=True)    #字典名称
    enums = db.relationship('SysEnum', back_populates='dict', cascade='all')
'''
    系统下拉字典枚举值
'''
class SysEnum(BaseModel, db.Model):
    value = db.Column(db.String(24))        #枚举值
    view = db.Column(db.String(128))        #显示值
    dict_id = db.Column(db.String(32), db.ForeignKey('sys_dict.id'))
    dict = db.relationship('SysDict', back_populates='enums')
'''
    系统日志表
'''
class SysLog(BaseModel, db.Model):
    url = db.Column(db.String(24))      #菜单url
    operate = db.Column(db.String(64))  #操作内容
    user_id = db.Column(db.String(32), db.ForeignKey('sys_user.id'))
    user = db.relationship('SysUser', back_populates='logs')