from flask import Blueprint, render_template, flash
from flask_login import current_user
from pm.forms.biz.document import ProgramDocumentForm
from pm.models import BizProgram
bp_doc = Blueprint('doc', __name__)
@bp_doc.route('/index', methods=['GET', 'POST'])
def index():
    form = ProgramDocumentForm()
    form.program.choices = get_programs()
    program_id = form.program.choices[0][0] if form.program.data is None else form.program.data
    print('Program selected : ', program_id)
    # 存在对应的项目的情况才执行SVN文档管理
    if program_id != '0':
        print('Get SVN Documents ...')
        svn_id = current_user.svn_id    # svn账号
        svn_pwd = current_user.svn_pwd  # svn密码
        if not svn_id:
            flash('当前用户没有维护SVN账号信息,请联系管理员！')
        else:
            program = BizProgram.query.get(program_id)
            svn_uri = program.svn               # svn地址
            if not svn_uri:
                flash('当前项目没有维护SVN地址信息！')
            else:
                pass
    return render_template('biz/document/index.html', form=form)
def get_programs():
    '''
    获取项目清单
    :return:
    '''
    # 自己负责的项目
    programs = current_user.programs
    # 所属项目
    members = current_user.program_members
    # 执行合并(自己创建的项目以及参与的项目)
    for member in members:
        for program in member.programs:
            if program not in programs:
                programs.append(program)
    program_list = []
    for program in programs:
        program_list.append((program.id, program.name))
    if program_list:
        return program_list
    else:
        return [('0', '---没有可选择的项目---')]