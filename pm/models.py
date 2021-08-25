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
    timestamp_utc = db.Column(db.DateTime, default=datetime.utcnow)     # 标准时间
    timestamp_loc = db.Column(db.DateTime, default=datetime.now)        # 本地时间
'''
    使用模型表建立用户自关联关系
    1. 可以获取创建时间
    2. 对象映射清晰，易于查询
'''
class SysUserCreator(BaseModel, db.Model):
    created_id = db.Column(db.String(32), db.ForeignKey('sys_user.id'))
    created = db.relationship('SysUser', foreign_keys=[created_id], back_populates='created', lazy='joined')            # 被创建者
    created_by_id = db.Column(db.String(32), db.ForeignKey('sys_user.id'))
    created_by = db.relationship('SysUser', foreign_keys=[created_by_id], back_populates='created_by', lazy='joined')   # 创建者
class SysUserUpdater(BaseModel, db.Model):
    updated_id = db.Column(db.String(32), db.ForeignKey('sys_user.id'))
    updated = db.relationship('SysUser', foreign_keys=[updated_id], back_populates='updated', lazy='joined')            # 被更新者
    updated_by_id = db.Column(db.String(32), db.ForeignKey('sys_user.id'))
    updated_by = db.relationship('SysUser', foreign_keys=[updated_by_id], back_populates='updated_by', lazy='joined')   # 更新者
'''
    系统用户
'''
class SysUser(BaseModel, db.Model, UserMixin):
    user_id = db.Column(db.String(16), unique=True) # 用户代码
    user_name = db.Column(db.String(24))            # 用户姓名
    user_pwd_hash = db.Column(db.String(128))       # 用户密码(加密后)
    svn_id = db.Column(db.String(24))               # svn账号
    svn_pwd = db.Column(db.String(24))              # svn密码
    #created_by = db.relationship('SysUser', secondary=user_creators, primaryjoin=(user_creators.c.creator_id == id), secondaryjoin=(user_creators.c.created_id == id), backref=db.backref('user_creators', lazy='dynamic'))
    #updated_by = db.relationship('SysUser', secondary=user_updaters, primaryjoin=(user_updaters.c.updater_id == id), secondaryjoin=(user_updaters.c.updated_id == id), backref=db.backref('user_updaters', lazy='dynamic'))
    created = db.relationship('SysUserCreator', foreign_keys=[SysUserCreator.created_id], back_populates='created', lazy='dynamic', cascade='all')              # 被创建者
    created_by = db.relationship('SysUserCreator', foreign_keys=[SysUserCreator.created_by_id], back_populates='created_by', lazy='dynamic', cascade='all')     # 创建者
    updated = db.relationship('SysUserUpdater', foreign_keys=[SysUserUpdater.updated_id], back_populates='updated', lazy='dynamic', cascade='all')              # 被修改者
    updated_by = db.relationship('SysUserUpdater', foreign_keys=[SysUserUpdater.updated_by_id], back_populates='updated_by', lazy='dynamic', cascade='all')     # 修改者
    role_id = db.Column(db.String(32), db.ForeignKey('sys_role.id'))    # 系统角色ID
    role = db.relationship('SysRole', back_populates='users')           # 系统角色
    dept_id = db.Column(db.String(32), db.ForeignKey('biz_dept.id'))    # 所属部门ID
    dept = db.relationship('BizDept', back_populates='users')           # 所属部门
    logs = db.relationship('SysLog', back_populates='user')             # 操作日志

    def set_password(self, password):
        self.user_pwd_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.user_pwd_hash, password)

    #设置创建者
    def set_created_by(self, user):
        creator = SysUserCreator(created=self, created_by=user)
        db.session.add(creator)
        db.session.commit()
    #获取创建者(只有一条记录)
    @property
    def get_created_by(self):
        return self.created_by.filter_by(created_id=self.id).first().created_by.user_name
    #设置更新者
    def set_updated_by(self, user):
        updater = SysUserUpdater(updated=self, updated_by=user)
        db.session.add(updater)
        db.session.commit()
    #获取更新者(零或多条记录，可能没有被更新过或者被多次更新过)
    @property
    def get_updated_by(self):
        return self.updated_by.filter_by(updated_id=self.id).order_by(SysUserUpdater.timestamp_utc.desc()).all()
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
    name = db.Column(db.String(64), unique=True)                # 角色名称
    users = db.relationship('SysUser', back_populates='role')   # 用户
    menus = db.relationship('SysMenu', secondary='roles_menus', back_populates='roles')
'''
    系统菜单
'''
class SysMenu(BaseModel, db.Model):
    name = db.Column(db.String(64))         # 菜单名
    url = db.Column(db.String(24))          # URL地址
    roles = db.relationship('SysRole', secondary='roles_menus', back_populates='menus')
'''
    下拉字典
'''
class SysDict(BaseModel, db.Model):
    code = db.Column(db.String(24), unique=True)    # 字典代码
    name = db.Column(db.String(24), unique=True)    # 字典名称
    enums = db.relationship('SysEnum', back_populates='dict', cascade='all')
'''
    下拉字典枚举值
'''
class SysEnum(BaseModel, db.Model):
    value = db.Column(db.String(24))        # 枚举值
    view = db.Column(db.String(128))        # 显示值
    dict_id = db.Column(db.String(32), db.ForeignKey('sys_dict.id'))
    dict = db.relationship('SysDict', back_populates='enums')
'''
    系统操作日志
'''
class SysLog(BaseModel, db.Model):
    url = db.Column(db.String(24))      # 菜单url
    operate = db.Column(db.String(64))  # 操作内容
    user_id = db.Column(db.String(32), db.ForeignKey('sys_user.id'))
    user = db.relationship('SysUser', back_populates='logs')
'''
    子部门
'''
class BizSubDept(BaseModel, db.Model):
    dept_id = db.Column(db.String(32), db.ForeignKey('biz_dept.id'))
    dept = db.relationship('BizDept', foreign_keys=[dept_id], back_populates='sub_dept', lazy='joined')
'''
    部门
'''
class BizDept(BaseModel, db.Model):
    code = db.Column(db.String(32), unique=True)                # 部门代码
    name = db.Column(db.String(128), unique=True)               # 部门名称
    users = db.relationship('SysUser', back_populates='dept')   # 部门人员
    sub_dept = db.relationship('BizSubDept', foreign_keys=[BizSubDept.dept_id], back_populates='dept', lazy='dynamic', cascade='all')  # 子部门