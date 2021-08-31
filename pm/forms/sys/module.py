from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired
from wtforms import ValidationError, validators
from pm.models import SysModule
class ModuleSearchForm(FlaskForm):
    name = StringField('模块名称', [validators.optional()])
class ModuleForm(FlaskForm):
    id = HiddenField()
    name = StringField('模块名称', validators=[DataRequired('请输入模块名称！')])

    def validate_name(self, field):
        if self.id.data == '':
            if SysModule.query.filter_by(name=field.data).first():
                raise ValidationError('模块名称已存在!')
        else:
            old_name = SysModule.query.get(self.id.data).name
            names = []
            for role in SysModule.query.all():
                names.append(role.name)
            # 剔除未更新前的模块名称
            names.remove(old_name)
            # Check新的模块名称是否已经存在
            if field.data in names:
                raise ValidationError('模块名称已存在!')