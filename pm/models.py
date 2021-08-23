from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from pm.plugins import db
import uuid, os
'''
    用户创建者自关系表
'''
user_creators = db.Table('user_creators',
    db.Column('creator_id', db.String(32), db.ForeignKey('user.id')),   #创建者ID
    db.Column('created_id', db.String(32), db.ForeignKey('user.id')),   #被创建者ID
    db.Column('created_time', db.DateTime, default=datetime.utcnow)     #创建时间
)
'''
    用户更新者自关系表
'''
user_updaters = db.Table('user_updaters',
    db.Column('updater_id', db.String(32), db.ForeignKey('user.id')),   #更新者ID
    db.Column('updated_id', db.String(32), db.ForeignKey('user.id')),   #被更新者ID
    db.Column('updated_time', db.DateTime, default=datetime.utcnow)     #更新时间
)
class User(db.Model, UserMixin):
    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(16), unique=True)
    user_name = db.Column(db.String(24))
    user_pwd_hash = db.Column(db.String(128))
    svn_id = db.Column(db.String(24))
    svn_pwd = db.Column(db.String(24))
    created_by = db.relationship('User', secondary=user_creators, primaryjoin=(user_creators.c.creator_id == id), secondaryjoin=(user_creators.c.created_id == id), backref=db.backref('user_creators', lazy='dynamic'))
    updated_by = db.relationship('User', secondary=user_updaters, primaryjoin=(user_updaters.c.updater_id == id), secondaryjoin=(user_updaters.c.updated_id == id), backref=db.backref('user_updaters', lazy='dynamic'))

    def set_password(self, password):
        self.user_pwd_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.user_pwd_hash, password)