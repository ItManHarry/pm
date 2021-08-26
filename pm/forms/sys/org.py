from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError, validators
from pm.models import BizDept
class OrgSearchForm(FlaskForm):
    code = StringField('部门代码', [validators.optional()])
    name = StringField('部门名称', [validators.optional()])
class OrgForm(FlaskForm):
    '''departments = BizDept.query.order_by(BizDept.code.desc()).all()
    department_list = []
    for department in departments:
        department_list.append((department.id, department.name))
    print('Dept list is >>>>>>>>>> ', department_list)
    '''
    code = StringField('部门代码', validators=[DataRequired('请输入部门代码！')])
    name = StringField('部门名称', validators=[DataRequired('请输入部门名称！')])
    parent = SelectField('上级部门', [validators.optional()], choices=[])

