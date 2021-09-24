from flask import Blueprint, render_template, session, request
from flask_login import login_required, current_user
from pm.decorators import log_record
from pm.forms.biz.issue import IssueForm, IssueSearchForm
from pm.utils import get_options
bp_issue = Blueprint('iss', __name__)
@bp_issue.route('/index', methods=['GET', 'POST'])
@login_required
@log_record('查看issue事项清单')
def index():
    form = IssueSearchForm()
    # 自己负责的项目
    programs = current_user.programs
    print('My programs are : >>>>>>>>>>>>>>>', programs)
    # 所属项目
    members = current_user.program_members
    print('Members are : >>>>>>>>>>>>>>>', members)
    # 执行合并
    for member in members:
        for program in member.programs:
            if program not in programs:
                programs.append(program)
    program_list = []
    program_list.append(('0', '---请选择---'))
    for program in programs:
        program_list.append((program.id, program.name))
    form.program.choices = program_list
    form.category.choices = [('0', '---请选择---')]+get_options('D006')
    form.grade.choices = [('0', '---请选择---')]+get_options('D007')
    form.state.choices = [('0', '---请选择---')]+get_options('D008')
    if request.method == 'GET':     # 获取所有的issue事项
        if programs:
            for program in programs:
                print('Program is : ', program.name)
                for member in program.members:
                    if member.member_id == current_user.id:
                        print('Person role is : ', member.pro_role.display)
            issues = []
            pagination = []
        else:
            issues = []
            pagination = []
    if request.method == 'POST':
        pro = form.program.data             # 所属项目
        category = form.category.data       # issue类别
        grade = form.grade.data             # issue等级
        state = form.state.data             # issue状态
        issues = []
        pagination = []
    return render_template('biz/issue/index.html', form=form, issues=issues, pagination=pagination)
@bp_issue.route('/add', methods=['GET', 'POST'])
@login_required
@log_record('新增issue事项')
def add():
    form = IssueForm()
    return render_template('biz/issue/add.html', form=form)