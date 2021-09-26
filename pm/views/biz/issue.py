from flask import Blueprint, render_template, request, current_app, jsonify
from flask_login import login_required, current_user
from pm.decorators import log_record
from pm.forms.biz.issue import IssueForm, IssueSearchForm
from pm.models import BizProgramIssue, BizProgramIssueLog, BizProgram
from pm.utils import get_options
bp_issue = Blueprint('iss', __name__)
@bp_issue.route('/index', methods=['GET', 'POST'])
@login_required
@log_record('查看issue事项清单')
def index():
    form = IssueSearchForm()
    program_id_list, program_list = get_programs('index')
    form.program.choices = program_list
    form.category.choices = [('0', '---请选择---')]+get_options('D006')
    form.grade.choices = [('0', '---请选择---')]+get_options('D007')
    form.state.choices = [('0', '---请选择---')]+get_options('D008')
    form.charge.choices = [('0', '---请选择---')]
    if request.method == 'GET':     # 获取所有的issue事项(注:前台页面控制不是自己负责的issue不能编辑)
        form.program.data = '0'
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['ITEM_COUNT_PER_PAGE']
        pagination = BizProgramIssue.query.filter(BizProgramIssue.program_id.in_(program_id_list)).order_by(BizProgramIssue.program_id).paginate(page, per_page)
        issues = pagination.items
    if request.method == 'POST':
        pro = form.program.data             # 所属项目
        category = form.category.data       # issue类别
        grade = form.grade.data             # issue等级
        state = form.state.data             # issue状态
        charge = form.charge.data           # issue担当
        if pro != '0':
            program = BizProgram.query.get_or_404(pro)
            members = []
            for member in program.members:
                members.append((member.member_id, member.member.user_name))
            form.charge.choices += members
        issues = []
        pagination = []
    # 前台添加链接是否可用(项目情况是否为空)
    disabled = False if program_id_list else True
    return render_template('biz/issue/index.html', form=form, issues=issues, pagination=pagination, disabled=disabled)
@bp_issue.route('/add/<pro_id>', methods=['GET', 'POST'])
@login_required
@log_record('新增issue事项')
def add(pro_id):
    print('Program id is : %s' %pro_id)
    form = IssueForm()
    program_id_list, program_list = get_programs('add')
    form.pro_id.choices = program_list
    if pro_id != '0':
        form.pro_id.data = pro_id
    else:
        form.pro_id.data = program_id_list[0]
    form.category_id.choices = get_options('D006')
    form.grade_id.choices = get_options('D007')
    form.state_id.choices = get_options('D008')
    program = BizProgram.query.get_or_404(form.pro_id.data)
    members = []
    for member in program.members:
        members.append((member.member_id, member.member.user_name))
    form.handler_id.choices = members
    return render_template('biz/issue/add.html', form=form)
@bp_issue.route('/pro/<pro_id>/members', methods=['POST'])
@login_required
def get_members(pro_id):
    program = BizProgram.query.get_or_404(pro_id)
    members = []
    for member in program.members:
        members.append((member.member_id, member.member.user_name))
    return jsonify(members=members)
'''
获取项目下拉清单(自己创建的项目及参与的项目集合)
sign:哪个页面获取项目清单 index:issue主页
'''
def get_programs(sign):
    # 自己负责的项目
    programs = current_user.programs
    # 所属项目
    members = current_user.program_members
    # 执行合并(自己创建的项目以及参与的项目)
    for member in members:
        for program in member.programs:
            if program not in programs:
                programs.append(program)
    program_id_list = []
    program_list = []
    if sign == 'index':
        program_list.append(('0', '---请选择---'))
    for program in programs:
        program_id_list.append(program.id)
        program_list.append((program.id, program.name))
    return program_id_list, program_list