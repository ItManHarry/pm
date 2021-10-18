from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms import validators
'''
项目清单
'''
class ProgramDocumentForm(FlaskForm):
    program = SelectField('项目', [validators.optional()], choices=[])