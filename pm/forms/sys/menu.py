from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from wtforms import ValidationError, validators
from pm.models import SysMenu
class MenuSearchForm(FlaskForm):
    name = StringField('菜单名称', [validators.optional()])
class MenuForm(FlaskForm):
    id = HiddenField()
    name = StringField('菜单名称', validators=[DataRequired('请输入菜单名称！')])
    url = StringField('菜单URL', validators=[DataRequired('请输入菜单URL地址！')])
    desc = TextAreaField('菜单说明', validators=[DataRequired('请输入菜单说明！')])
    module = SelectField('所属模块', validators=[DataRequired('请选择所属模块！')], choices=[])
    icon = StringField('菜单图标', [validators.optional()])

    def validate_name(self, field):
        if self.id.data == '':
            if SysMenu.query.filter_by(name=field.data).first():
                raise ValidationError('菜单名称已存在!')
        else:
            old_name = SysMenu.query.get(self.id.data).name
            names = []
            for menu in SysMenu.query.all():
                names.append(menu.name)
            # 剔除未更新前的菜单名称
            names.remove(old_name)
            # Check新的菜单名称是否已经存在
            if field.data in names:
                raise ValidationError('菜单名称已存在!')