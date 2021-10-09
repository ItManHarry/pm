from flask import Blueprint, render_template, request, current_app, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from pm.decorators import log_record
from pm.forms.biz.issue import IssueForm, IssueSearchForm
from pm.plugins import db
from pm.models import BizProgramIssue, BizProgramIssueLog, BizProgram
from pm.utils import get_options, format_time, get_current_user
import uuid
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
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    if request.method == 'GET':     # 获取所有的issue事项(注:前台页面控制不是自己负责的issue不能编辑)
        form.program.data = '0'
        pagination = BizProgramIssue.query.filter(BizProgramIssue.program_id.in_(program_id_list)).order_by(BizProgramIssue.program_id).paginate(page, per_page)
    if request.method == 'POST':
        # 所属项目
        pro = form.program.data
        # 使用集合存储查询条件
        conditions = set()
        # issue类别
        if form.category.data != '0':
            conditions.add(BizProgramIssue.category_id==form.category.data)
        # issue等级
        if form.grade.data !='0':
            conditions.add(BizProgramIssue.grade_id==form.grade.data)
        # issue状态
        if form.state.data != '0':
            conditions.add(BizProgramIssue.state_id == form.state.data)
        # issue担当
        if form.charge.data != '0':
            conditions.add(BizProgramIssue.handler_id == form.charge.data)
        # 某个项目的issue清单
        if pro != '0':
            program = BizProgram.query.get_or_404(pro)
            members = []
            for member in program.members:
                members.append((member.member_id, member.member.user_name))
            form.charge.choices += members
            if conditions:
                pagination = BizProgramIssue.query.with_parent(program).filter(*conditions).order_by(BizProgramIssue.timestamp_loc).paginate(page, per_page)
            else:
                pagination = BizProgramIssue.query.with_parent(program).order_by(BizProgramIssue.timestamp_loc).paginate(page, per_page)
        else:
            conditions.add(BizProgramIssue.program_id.in_(program_id_list))
            pagination = BizProgramIssue.query.filter(*conditions).order_by(BizProgramIssue.program_id).paginate(page, per_page)
    issues = pagination.items
    # 前台添加链接是否可用(项目清单是否为空)
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
    if request.method == 'GET':
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
    if form.validate_on_submit():
        issue = BizProgramIssue(
            id=uuid.uuid4().hex,
            program=program,
            category_id=form.category_id.data,
            grade_id=form.grade_id.data,
            state_id=form.state_id.data,
            description=form.description.data,
            handler_id=form.handler_id.data,
            ask_finish_dt=form.ask_finish_dt.data,
            operator_id=current_user.id
        )
        db.session.add(issue)
        db.session.commit()
        # 添加日志
        log = BizProgramIssueLog(
            id=uuid.uuid4().hex,
            issue=issue,
            content='新增issue',
            operator_id=current_user.id
        )
        db.session.add(log)
        db.session.commit()
        flash('ISSUE新增成功！')
        return redirect(url_for('.add', pro_id=form.pro_id.data))
    return render_template('biz/issue/add.html', form=form)
@bp_issue.route('/edit/<issue_id>', methods=['GET', 'POST'])
@login_required
@log_record('修改issue事项')
def edit(issue_id):
    issue = BizProgramIssue.query.get_or_404(issue_id)
    state_before_update = issue.state.display
    form = IssueForm()
    program_id_list, program_list = get_programs('edit')
    form.pro_id.choices = program_list
    form.category_id.choices = get_options('D006')
    form.grade_id.choices = get_options('D007')
    form.state_id.choices = get_options('D008')
    members = []
    for member in issue.program.members:
        members.append((member.member_id, member.member.user_name))
    form.handler_id.choices = members
    if request.method == 'GET':
        form.id.data = issue.program_id
        form.pro_id.data = issue.program_id
        form.category_id.data = issue.category_id
        form.grade_id.data = issue.grade_id
        form.state_id.data = issue.state_id
        form.description.data = issue.description
        form.handler_id.data = issue.handler_id
        form.ask_finish_dt.data = issue.ask_finish_dt
    if form.validate_on_submit():
        issue.category_id = form.category_id.data
        issue.grade_id = form.grade_id.data
        issue.state_id = form.state_id.data
        issue.description = form.description.data
        issue.handler_id = form.handler_id.data
        issue.ask_finish_dt = form.ask_finish_dt.data
        db.session.commit()
        state_after_update = issue.state.display
        if state_before_update == state_after_update:
            content = '修改issue信息'
        else:
            content = '将issue状态由('+state_before_update+')变更为('+state_after_update+')'
        # 添加日志
        log = BizProgramIssueLog(
            id=uuid.uuid4().hex,
            issue=issue,
            content=content,
            operator_id=current_user.id
        )
        db.session.add(log)
        db.session.commit()
        flash('ISSUE信息更改成功！')
        return redirect(url_for('.edit', issue_id=issue_id))
    return render_template('biz/issue/edit.html', form=form)
@bp_issue.route('/pro/<pro_id>/members', methods=['POST'])
@login_required
def get_members(pro_id):
    program = BizProgram.query.get_or_404(pro_id)
    members = []
    for member in program.members:
        members.append((member.member_id, member.member.user_name))
    return jsonify(members=members)
@bp_issue.route('/logs/<issue_id>', methods=['POST'])
@login_required
def get_logs(issue_id):
    issue = BizProgramIssue.query.get_or_404(issue_id)
    logs = BizProgramIssueLog.query.with_parent(issue).order_by(BizProgramIssueLog.timestamp_loc.desc()).all()
    log_list = []
    for log in logs:
        log_list.append((get_current_user(log.operator_id).user_name, log.content, format_time(log.timestamp_utc)))
    return jsonify(logs=log_list)
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