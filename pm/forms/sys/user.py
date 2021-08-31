from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from wtforms import ValidationError, validators
from pm.models import SysUser
class UserSearchForm(FlaskForm):
    code = StringField('用户代码', [validators.optional()])
    name = StringField('用户姓名', [validators.optional()])
class UserForm(FlaskForm):
    id = HiddenField()
    code = StringField('用户代码', validators=[DataRequired('请输入用户代码！')])
    name = StringField('用户姓名', validators=[DataRequired('请输入用户姓名！')])
    password = PasswordField('密码', validators=[DataRequired('请输入密码!!!'), Length(8, 128, '长度要介于8~128!!!'), EqualTo('password_confirm', message='密码不一致!!!'), Regexp('^(?:(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).*$', message='密码必须包含大小写字母和数字!!!')])
    password_confirm = PasswordField('确认密码', validators=[DataRequired('请确认密码!!!')])
    email = StringField('邮箱', validators=[DataRequired('请输入邮箱!!!'), Length(1, 64, '长度要介于1~64!!!'), Email('邮箱格式不正确!!!')])
    svn_id = StringField('SVN账号', [validators.optional()])
    svn_pwd = PasswordField('SVN密码', [validators.optional()])
    role = SelectField('角色', validators=[DataRequired('请选择角色！')], choices=[])
    dept = SelectField('部门', validators=[DataRequired('请选择部门！')], choices=[])

    def validate_code(self, field):
        if self.id.data == '':
            if SysUser.query.filter_by(user_id=field.data.lower()).first():
                raise ValidationError('用户代码已存在!')
        else:
            old_code = SysUser.query.get(self.id.data).user_id
            codes = []
            all_users = SysUser.query.all()
            for user in all_users:
                codes.append(user.user_id)
            # 剔除未更新前的用户代码
            codes.remove(old_code)
            # Check新的用户代码是否已经存在
            if field.data.lower() in codes:
                raise ValidationError('人员代码已存在!')

    def validate_email(self, field):
        if self.id.data == '':
            if SysUser.query.filter_by(email=field.data.lower()).first():
                raise ValidationError('邮箱地址已存在!')
        else:
            old_email = SysUser.query.get(self.id.data).email
            emails = []
            for user in SysUser.query.all():
                emails.append(user.email)
            # 剔除未更新前的邮箱地址
            emails.remove(old_email)
            # Check新的邮箱地址是否已经存在
            if field.data in emails:
                raise ValidationError('邮箱地址已存在!')