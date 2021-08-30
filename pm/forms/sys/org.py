from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError, validators
from pm.models import BizDept
class OrgSearchForm(FlaskForm):
    code = StringField('部门代码', [validators.optional()])
    name = StringField('部门名称', [validators.optional()])
class OrgForm(FlaskForm):
    '''
    以下使用会报错：
    RuntimeError: No application found. Either work inside a view function or push an application context. See http://flask-sqlalchemy.pocoo.org/contexts/.
    原因：当前未装入Flask应用上下文，顾数据库操作不可用
    '''
    '''
    departments = BizDept.query.order_by(BizDept.code.desc()).all()
    for department in departments:
        department_list.append((department.id, department.name))
    print('Dept list is >>>>>>>>>> ', department_list)
    '''
    #department_list = []
    id = HiddenField()
    code = StringField('部门代码', validators=[DataRequired('请输入部门代码！')])
    name = StringField('部门名称', validators=[DataRequired('请输入部门名称！')])
    parent = SelectField('上级部门', [validators.optional()], choices=[])
    has_parent = HiddenField()      # 是否有上级部门(1:有 0：没有， 默认为有)

    def validate_code(self, field):
        if self.id.data == '':
            if BizDept.query.filter_by(code=field.data.lower()).first():
                raise ValidationError('部门代码已存在!')
        else:
            old_code = BizDept.query.get(self.id.data).code
            codes = []
            all_departments = BizDept.query.all()
            for department in all_departments:
                codes.append(department.code)
            # 剔除未更新前的部门代码
            codes.remove(old_code)
            # Check新的部门代码是否已经存在
            if field.data.lower() in codes:
                raise ValidationError('部门代码已存在!')
    def validate_name(self, field):
        if self.id.data == '':
            if BizDept.query.filter_by(name=field.data).first():
                raise ValidationError('部门名称已存在!')
        else:
            old_name = BizDept.query.get(self.id.data).name
            names = []
            for department in BizDept.query.all():
                names.append(department.name)
            # 剔除未更新前的部门名称
            names.remove(old_name)
            # Check新的部门名称是否已经存在
            if field.data in names:
                raise ValidationError('部门名称已存在!')