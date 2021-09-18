from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField, SelectField, IntegerField, FloatField, BooleanField, DateField
from wtforms.validators import DataRequired, NumberRange
from wtforms import ValidationError, validators
from pm.models import BizProgram
'''
项目搜索表单
'''
class ProgramSearchForm(FlaskForm):
    no = StringField('项目编号', [validators.optional()])
    name = StringField('项目名称', [validators.optional()])
'''
项目主信息表单
'''
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
'''
项目成员表单
'''
class ProgramMemberForm(FlaskForm):
    pro_id = HiddenField()                                                                              # 项目ID
    pro_roles = SelectField('成员角色', [validators.optional()], choices=[])                             # 项目人员角色
    user_dept = SelectField('部门所属', [validators.optional()], choices=[])                             # 人员组织
    for_select = SelectField('选择成员', [validators.optional()], choices=[])                            # 待选人员
    selected = SelectField('已选成员',   [validators.optional()], choices=[])                            # 已选人员
'''
项目状态表单
'''
class ProgramStatusForm(FlaskForm):
    pro_id = HiddenField()
    enterprise = StringField('法人', validators=[DataRequired('请填写法人！')])
    client = StringField('客户公司', validators=[DataRequired('请填写客户公司！')])
    client_dept = StringField('客户公司主管部门', validators=[DataRequired('请填写客户公司主管部门！')])
    charge_dept = StringField('公司负责部门', validators=[DataRequired('请填写公司负责部门！')])
    new = BooleanField('是否新项目')
    clazz_id = SelectField('项目分类', validators=[DataRequired('请选择项目分类！')], choices=[])
    state_id = SelectField('项目状态', validators=[DataRequired('请选择项目状态！')], choices=[])
    odds = IntegerField('执行可能性(%)', validators=[DataRequired('执行可能性只能是1~100的数字！'), NumberRange(min=1, max=100, message='执行可能性只能介于1~100！')])
    con_start = DateField('合同开始日期', validators=[DataRequired('请填写合同开始日期！')])
    con_end = DateField('合同结束日期', validators=[DataRequired('请填写合同结束日期！')])
    process_now = StringField('进行现况', validators=[DataRequired('请填写进行现况！')])
    budget = FloatField('事业预算', validators=[DataRequired('事业预算只能是数字！'), NumberRange(message='请输入数字！')])
'''
项目发票表单
'''
class ProgramInvoiceForm(FlaskForm):
    pro_id = HiddenField()
    invoice_id = HiddenField()
    category_id = SelectField('发票类别', validators=[DataRequired('请选择发票类别！')], choices=[])
    percent = IntegerField('支付比例(%)', validators=[DataRequired('支付比例只能是1~100的数字！'), NumberRange(min=1, max=100, message='支付比例只能介于1~100！')])
    make_out = BooleanField('已开票')
    make_out_dt = DateField('开票日期', format='%Y-%m-%d', validators=[DataRequired('请填写开票日期！')])
    delivery_dt = DateField('验收日期', format='%Y-%m-%d', validators=[DataRequired('请填写验收日期！')])
    remark = TextAreaField('备注', [validators.optional()])
    '''
    def validate_make_out_dt(self, field):
        if self.make_out.data:
            if field.data is None:
                raise ValidationError(message='请填写开票日期！')

    def validate_delivery_dt(self, field):
        if self.make_out.data:
            if field.data is None:
                raise ValidationError(message='请填写验收日期！')
    '''
    def validate_percent(self, field):
        program = BizProgram.query.get_or_404(self.pro_id.data)
        if program.invoices:
            payed = 0
            for invoice in program.invoices:
                if invoice.id != self.invoice_id.data:
                    payed += invoice.percent
            payed += field.data
            if payed > 100:
                raise ValidationError('支付比例总和超过了100,请修改！')