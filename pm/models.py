from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from pm.plugins import db
import uuid
'''
基础模型
'''
class BaseModel():
    id = db.Column(db.String(32), primary_key=True)
    timestamp_utc = db.Column(db.DateTime, default=datetime.utcnow)     # 标准时间
    timestamp_loc = db.Column(db.DateTime, default=datetime.now)        # 本地时间
    operator_id = db.Column(db.String(32))                              # 操作人员
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
    status = db.Column(db.Boolean, default=True)    # 用户状态(默认在用)
    email = db.Column(db.String(128))               # 邮箱
    svn_id = db.Column(db.String(24))               # svn账号
    svn_pwd = db.Column(db.String(24))              # svn密码
    #created_by = db.relationship('SysUser', secondary=user_creators, primaryjoin=(user_creators.c.creator_id == id), secondaryjoin=(user_creators.c.created_id == id), backref=db.backref('user_creators', lazy='dynamic'))
    #updated_by = db.relationship('SysUser', secondary=user_updaters, primaryjoin=(user_updaters.c.updater_id == id), secondaryjoin=(user_updaters.c.updated_id == id), backref=db.backref('user_updaters', lazy='dynamic'))
    created = db.relationship('SysUserCreator', foreign_keys=[SysUserCreator.created_id], back_populates='created', lazy='dynamic', cascade='all')              # 被创建者
    created_by = db.relationship('SysUserCreator', foreign_keys=[SysUserCreator.created_by_id], back_populates='created_by', lazy='dynamic', cascade='all')     # 创建者
    updated = db.relationship('SysUserUpdater', foreign_keys=[SysUserUpdater.updated_id], back_populates='updated', lazy='dynamic', cascade='all')              # 被修改者
    updated_by = db.relationship('SysUserUpdater', foreign_keys=[SysUserUpdater.updated_by_id], back_populates='updated_by', lazy='dynamic', cascade='all')     # 修改者
    role_id = db.Column(db.String(32), db.ForeignKey('sys_role.id'))                    # 系统角色ID
    role = db.relationship('SysRole', back_populates='users')                           # 系统角色
    dept_id = db.Column(db.String(32), db.ForeignKey('biz_dept.id'))                    # 所属部门ID
    dept = db.relationship('BizDept', back_populates='users')                           # 所属部门
    programs = db.relationship('BizProgram', back_populates='owner')                    # 负责项目清单
    program_members = db.relationship('BizProgramMember', back_populates='member')      # 项目成员
    issue_handlers = db.relationship('BizProgramIssue', back_populates='handler') # ISSUE处理人员
    logs = db.relationship('SysLog', back_populates='user')                             # 操作日志


    def set_password(self, password):
        self.user_pwd_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.user_pwd_hash, password)

    #设置创建者
    def set_created_by(self, user):
        creator = SysUserCreator(id=uuid.uuid4().hex, created=self, created_by=user, operator_id=user.id)
        db.session.add(creator)
        db.session.commit()
    #获取创建者(只有一条记录)
    @property
    def who_created(self):
        '''
        返回SysUser对象
        :return:
        '''
        return self.created_by.filter_by(created_id=self.id).first().created_by
    #设置更新者
    def set_updated_by(self, user):
        updater = SysUserUpdater(id=uuid.uuid4().hex, updated=self, updated_by=user, operator_id=user.id)
        db.session.add(updater)
        db.session.commit()
    #获取更新者(零或多条记录，可能没有被更新过或者被多次更新过)
    @property
    def who_updated(self):
        '''
        返回SysUser列表，按照时间降序排序
        :return:
        '''
        return self.updated_by.filter_by(updated_id=self.id).order_by(SysUserUpdater.timestamp_utc.desc()).all()
'''
角色菜单关联表(多对多)
'''
rel_role_menu = db.Table('rel_role_menu',
    db.Column('role_id', db.String(32), db.ForeignKey('sys_role.id')),
    db.Column('menu_id', db.String(32), db.ForeignKey('sys_menu.id'))
)
'''
系统角色
'''
class SysRole(BaseModel, db.Model):
    name = db.Column(db.String(64), unique=True)                # 角色名称
    users = db.relationship('SysUser', back_populates='role')   # 用户
    menus = db.relationship('SysMenu', secondary='rel_role_menu', back_populates='roles')
'''
系统模块
'''
class SysModule(BaseModel, db.Model):
    code = db.Column(db.String(12), unique=True)                # 模块代码(用以导航状态)
    name = db.Column(db.String(24), unique=True)                # 模块名称
    default_url = db.Column(db.String(24))                      # 默认链接URL地址
    menus = db.relationship('SysMenu', back_populates='module') # 和菜单建立一对多关联关系
'''
系统菜单
'''
class SysMenu(BaseModel, db.Model):
    name = db.Column(db.String(64))                 # 菜单名
    url = db.Column(db.String(24))                  # URL地址
    desc = db.Column(db.String(128))                # 菜单描述
    status = db.Column(db.Boolean, default=True)    # 菜单状态(是否在用,默认在用)
    icon = db.Column(db.String(24))                 # 图标
    module_id = db.Column(db.String(32), db.ForeignKey('sys_module.id'))
    module = db.relationship('SysModule', back_populates='menus')
    roles = db.relationship('SysRole', secondary='rel_role_menu', back_populates='menus')
'''
下拉字典
'''
class SysDict(BaseModel, db.Model):
    code = db.Column(db.String(24), unique=True)    # 字典代码
    name = db.Column(db.String(24), unique=True)    # 字典名称
    enums = db.relationship('SysEnum', back_populates='dictionary', cascade='all')
'''
下拉字典枚举值
'''
class SysEnum(BaseModel, db.Model):
    key = db.Column(db.String(8))                                                               # 枚举key
    display = db.Column(db.String(128))                                                         # 显示值
    dict_id = db.Column(db.String(32), db.ForeignKey('sys_dict.id'))                            # 所属字典ID
    dictionary = db.relationship('SysDict', back_populates='enums')                             # 所属字典
    program_member_role = db.relationship('BizProgramMember', back_populates='pro_role')        # 关联项目成员表(项目成员类型)
    program_clazz = db.relationship('BizProgramStatus', back_populates='clazz', lazy=True,
                                    primaryjoin='BizProgramStatus.clazz_id == SysEnum.id')      # 项目类别
    program_state = db.relationship('BizProgramStatus', back_populates='state', lazy=True,
                                    primaryjoin='BizProgramStatus.state_id == SysEnum.id')      # 项目状态
    program_invoice = db.relationship('BizProgramInvoice', back_populates='category')           # 关联项目成员表(项目成员类型)
    issue_category = db.relationship('BizProgramIssue', back_populates='category', lazy=True,
                                    primaryjoin='BizProgramIssue.category_id == SysEnum.id')    # ISSUE类型
    issue_grade = db.relationship('BizProgramIssue', back_populates='grade', lazy=True,
                                    primaryjoin='BizProgramIssue.grade_id == SysEnum.id')       # ISSUE等级
    issue_state = db.relationship('BizProgramIssue', back_populates='state', lazy=True,
                                    primaryjoin='BizProgramIssue.state_id == SysEnum.id')       # ISSUE状态
'''
系统操作日志
'''
class SysLog(BaseModel, db.Model):
    url = db.Column(db.String(24))          # 菜单url
    operation = db.Column(db.String(64))    # 操作内容
    user_id = db.Column(db.String(32), db.ForeignKey('sys_user.id'))
    user = db.relationship('SysUser', back_populates='logs')
'''
部门层级关系
'''
class BizDeptRel(BaseModel, db.Model):
    parent_dept_id = db.Column(db.String(32), db.ForeignKey('biz_dept.id'))
    parent_dept = db.relationship('BizDept', foreign_keys=[parent_dept_id], back_populates='parent_dept', lazy='joined') # 父部门
    child_dept_id = db.Column(db.String(32), db.ForeignKey('biz_dept.id'))
    child_dept = db.relationship('BizDept', foreign_keys=[child_dept_id], back_populates='child_dept', lazy='joined')   # 子部门
'''
部门
'''
class BizDept(BaseModel, db.Model):
    code = db.Column(db.String(32), unique=True)                # 部门代码
    name = db.Column(db.String(128), unique=True)               # 部门名称
    status = db.Column(db.Boolean, default=True)                # 部门状态(是否在用,默认在用)
    users = db.relationship('SysUser', back_populates='dept')   # 部门人员
    parent_dept = db.relationship('BizDeptRel', foreign_keys=[BizDeptRel.parent_dept_id], back_populates='parent_dept', lazy='dynamic', cascade='all')  # 父部门
    child_dept = db.relationship('BizDeptRel', foreign_keys=[BizDeptRel.child_dept_id], back_populates='child_dept', lazy='dynamic', cascade='all')     # 子部门
    # 设置父部门
    def set_parent_dept(self, dept):
        '''
        逻辑：首先判断是否已经维护父部门，如果存在则执行删除后新增
        :param dept:
        :return:
        '''
        ref = BizDeptRel.query.filter_by(child_dept_id=self.id).first()
        if ref:
            db.session.delete(ref)
            db.session.commit()
        parent = BizDeptRel(id=uuid.uuid4().hex, child_dept=self, parent_dept=dept)
        db.session.add(parent)
        db.session.commit()
    @property
    def my_parent_dept(self):
        dept = BizDeptRel.query.filter_by(child_dept_id=self.id).first()
        return dept.parent_dept if dept else None
    #设置子部门
    def set_child_dept(self, dept):
        '''
        逻辑：首先解除子部门原有的部门关系，然后再添加到当前部门下
        :param dept:
        :return:
        '''
        ref = BizDeptRel.query.filter_by(child_dept_id=dept.id).first()
        if ref:
            db.session.delete(ref)
            db.session.commit()
        child = BizDeptRel(id=uuid.uuid4().hex, child_dept=dept, parent_dept=self)
        db.session.add(child)
        db.session.commit()
    @property
    def my_child_dept(self):
        return BizDeptRel.query.filter_by(parent_dept_id=self.id).order_by(BizDeptRel.timestamp_loc.desc()).all()
'''
项目和项目成员关联表(多对多)
'''
rel_program_member = db.Table('rel_program_member',
    db.Column('program_id', db.String(32), db.ForeignKey('biz_program.id')),
    db.Column('member_id',  db.String(32), db.ForeignKey('biz_program_member.id'))
)
'''
项目主信息
'''
class BizProgram(BaseModel, db.Model):
    no = db.Column(db.String(24), unique=True)      # 项目编号
    name = db.Column(db.String(128))                # 项目名称
    pr = db.Column(db.String(24))                   # PR编号
    contract = db.Column(db.String(24))             # 合同编号
    desc = db.Column(db.Text())                     # 项目描述
    svn = db.Column(db.String(128))                 # SVN地址
    owner_id = db.Column(db.String(32), db.ForeignKey('sys_user.id'))   # 项目负责人ID
    owner = db.relationship('SysUser', back_populates='programs')       # 项目负责人
    members = db.relationship('BizProgramMember', secondary='rel_program_member', back_populates='programs')    # 项目成员(多对多)
    status = db.relationship('BizProgramStatus', uselist=False)                                                 # 项目状态(一对一)
    invoices = db.relationship('BizProgramInvoice', back_populates='program')                                   # 项目发票(一对多)
    issues = db.relationship('BizProgramIssue', back_populates='program')                                       # 项目ISSUE(一对多)
'''
项目成员信息
'''
class BizProgramMember(BaseModel, db.Model):
    pro_role_id = db.Column(db.String(32), db.ForeignKey('sys_enum.id'))                                    # 关联枚举表(字典ID:D002)
    pro_role = db.relationship('SysEnum', back_populates='program_member_role')                             # 项目角色-关联枚举
    member_id = db.Column(db.String(32), db.ForeignKey('sys_user.id'))                                      # 用户ID
    member = db.relationship('SysUser', back_populates='program_members')                                   # 关联用户
    programs = db.relationship('BizProgram', secondary='rel_program_member', back_populates='members')      # 所属项目
'''
项目状态信息
'''
class BizProgramStatus(BaseModel, db.Model):
    program_id = db.Column(db.String(32), db.ForeignKey('biz_program.id'))
    program = db.relationship('BizProgram', back_populates='status')                                            # 对应项目
    enterprise = db.Column(db.String(128))                                                                      # 法人
    client = db.Column(db.String(128))                                                                          # 客户公司
    client_dept = db.Column(db.String(128))                                                                     # 客户公司主管部门
    charge_dept = db.Column(db.String(128))                                                                     # 公司主管部门
    new = db.Column(db.Boolean, default=True)                                                                   # 是否新项目
    clazz_id = db.Column(db.String(32), db.ForeignKey('sys_enum.id'))                                           # 关联枚举表(字典ID:D004)
    clazz = db.relationship('SysEnum', back_populates='program_clazz', lazy=True, foreign_keys=[clazz_id])      # 项目分类
    state_id = db.Column(db.String(32), db.ForeignKey('sys_enum.id'))                                           # 关联枚举表(字典ID:D003)
    state = db.relationship('SysEnum', back_populates='program_state', lazy=True, foreign_keys=[state_id])      # 项目状态
    odds = db.Column(db.Integer)                                                                                # 执行几率
    con_start = db.Column(db.Date())                                                                            # 合同开始日期
    con_end = db.Column(db.Date())                                                                              # 合同结束日期
    process_now = db.Column(db.String(32))                                                                      # 项目进行现况
    budget = db.Column(db.Float)                                                                                # 事业预算
class BizProgramInvoice(BaseModel, db.Model):
    program_id = db.Column(db.String(32), db.ForeignKey('biz_program.id'))
    program = db.relationship('BizProgram', back_populates='invoices')                      # 对应项目
    category_id = db.Column(db.String(32), db.ForeignKey('sys_enum.id'))                    # 关联枚举表(字典ID:D005)
    category = db.relationship('SysEnum', back_populates='program_invoice')                 # 发票类别-关联枚举
    percent = db.Column(db.Integer)                                                         # 支付比例
    make_out = db.Column(db.Boolean, default=False)                                         # 已开票
    make_out_dt = db.Column(db.Date())                                                      # 开票日期
    delivery_dt = db.Column(db.Date())                                                      # 验收日期
    remark = db.Column(db.Text())                                                           # 备注
class BizProgramIssue(BaseModel, db.Model):
    program_id = db.Column(db.String(32), db.ForeignKey('biz_program.id'))
    program = db.relationship('BizProgram', back_populates='issues')                                                    # 对应项目
    category_id = db.Column(db.String(32), db.ForeignKey('sys_enum.id'))                                                # 关联枚举表(字典ID:D006)
    category = db.relationship('SysEnum', back_populates='issue_category', lazy=True, foreign_keys=[category_id])       # ISSUE类别
    grade_id = db.Column(db.String(32), db.ForeignKey('sys_enum.id'))                                                   # 关联枚举表(字典ID:D007)
    grade = db.relationship('SysEnum', back_populates='issue_grade', lazy=True, foreign_keys=[grade_id])                # ISSUE等级
    state_id = db.Column(db.String(32), db.ForeignKey('sys_enum.id'))                                                   # 关联枚举表(字典ID:D008)
    state = db.relationship('SysEnum', back_populates='issue_state', lazy=True, foreign_keys=[state_id])                # ISSUE处理状态
    description = db.Column(db.Text())                                                                                  # ISSUE描述
    handler_id = db.Column(db.String(32), db.ForeignKey('sys_user.id'))                                                 # ISSUE处理人员ID
    handler = db.relationship('SysUser', back_populates='issue_handlers')                                               # ISSUE处理人员
    ask_finish_dt = db.Column(db.Date())                                                                                # 邀请完成日期
    real_finish_dt = db.Column(db.Date())                                                                               # 实际完成日期
    logs = db.relationship('BizProgramIssueLog', back_populates='issue')                                                # issue处理日志
class BizProgramIssueLog(BaseModel, db.Model):
    issue_id = db.Column(db.String(32), db.ForeignKey('biz_program_issue.id'))
    issue = db.relationship('BizProgramIssue', back_populates='logs')               # 所属issue
    content = db.Column(db.Text())                                                  # 操作事项