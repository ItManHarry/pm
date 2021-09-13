from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField, SelectField
from wtforms.validators import DataRequired
from wtforms import ValidationError, validators
from pm.models import BizProgram
class ProgramSearchForm(FlaskForm):
    no = StringField('项目编号', [validators.optional()])
    name = StringField('项目名称', [validators.optional()])
class ProgramForm(FlaskForm):
    id = HiddenField()
    no = StringField('项目编号', [validators.optional()]) # 项目编号自动生成
    name = StringField('项目名称', validators=[DataRequired('请输入项目名称！')])
    pr = StringField('PR编号', [validators.optional()])
    contract = StringField('合同编号', [validators.optional()])
    svn = StringField('SVN地址', [validators.optional()])
    desc = TextAreaField('项目描述', [validators.optional()])

    def validate_name(self, field):
        if self.id.data == '':
            if BizProgram.query.filter_by(name=field.data).first():
                raise ValidationError('项目名称已存在!')
        else:
            old_name = BizProgram.query.get(self.id.data).name
            names = []
            for program in BizProgram.query.all():
                names.append(program.name)
            # 剔除未更新前的部门名称
            names.remove(old_name)
            # Check新的部门名称是否已经存在
            if field.data in names:
                raise ValidationError('项目名称已存在!')
class ProgramMemberForm(FlaskForm):
    pro_id = HiddenField()                                                                              # 项目ID
    pro_roles = SelectField('成员角色', [validators.optional()], choices=[])                             # 项目人员角色
    for_select = SelectField('选择成员', [validators.optional()], choices=[])                            # 待选人员
    selected = SelectField('已选成员',   [validators.optional()], choices=[])                            # 已选人员