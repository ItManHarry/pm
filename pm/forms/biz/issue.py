from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, TextAreaField, HiddenField, SelectField, IntegerField, FloatField, BooleanField, DateField
from wtforms.validators import DataRequired, NumberRange
from wtforms import ValidationError, validators
from pm.models import BizProgram
'''
ISSUE搜索表单
'''
class IssueSearchForm(FlaskForm):
    program = SelectField('项目', [validators.optional()], choices=[])
    category = SelectField('类别', [validators.optional()], choices=[])
    grade = SelectField('等级', [validators.optional()], choices=[])
    state = SelectField('状态', [validators.optional()], choices=[])
    charge = SelectField('担当', [validators.optional()], choices=[])
'''
ISSUE信息表单
'''
class IssueForm(FlaskForm):
    id = HiddenField()
    pro_id = SelectField('项目', validators=[DataRequired('请选择项目！')], choices=[])
    category_id = SelectField('类别', validators=[DataRequired('请选择类别！')], choices=[])
    grade_id = SelectField('等级', validators=[DataRequired('请选择等级！')], choices=[])
    state_id = SelectField('状态', validators=[DataRequired('请选择状态！')], choices=[])
    description = CKEditorField('描述', validators=[DataRequired('请输入描述!')])
    handler_id = SelectField('处理人员', validators=[DataRequired('请选择处理人员！')], choices=[])
    ask_finish_dt = DateField('邀请完成日期', validators=[DataRequired('请填写邀请完成日期')])