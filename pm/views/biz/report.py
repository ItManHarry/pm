from flask import Blueprint, current_app, render_template, url_for, request, session
from flask_login import login_required, current_user
from pm.models import BizProgram, BizProgramIssue, SysUser
from pm.forms.biz.program import ProgramSearchForm
from pm.forms.biz.issue import IssueSearchForm
from pm.decorators import log_record
from pm.utils import get_options, get_current_user
import flask_excel as excel
bp_report = Blueprint('rpt', __name__)
@bp_report.route('/program', methods=['GET', 'POST'])
@login_required
@log_record('查看项目报表')
def program():
    form = ProgramSearchForm()
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        try:
            no = session['program_search_no'] if session['program_search_no'] else ''       # 项目编号
            name = session['program_search_nm'] if session['program_search_nm'] else ''     # 项目名称
        except KeyError:
            no = ''
            name = ''
        form.no.data = no
        form.name.data = name
    if request.method == 'POST':
        page = 1
        no = form.no.data
        name = form.name.data
        session['program_search_no'] = no
        session['program_search_nm'] = name
    session['program_current_page'] = page
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    pagination = BizProgram.query.filter(BizProgram.no.like('%' + no + '%'), BizProgram.name.like('%' + name + '%')).order_by(BizProgram.timestamp_loc).paginate(page, per_page)
    programs = pagination.items
    return render_template('biz/report/program/index.html', form=form, programs=programs, pagination=pagination)
@bp_report.route('/program/excel/export/<int:sign>', methods=['GET'])
@login_required
@log_record('导出项目报表')
def export_program(sign):
    '''
    Program清单导出
    :param sign: 0:导出全部 1:导出当前页
    :return:
    '''
    excel.init_excel(current_app)
    # 查询条件
    print('No : %s, name %s ' %(session['program_search_no'], session['program_search_nm']))
    no = session['program_search_no']
    name = session['program_search_nm']
    if sign == 0:
        program_data = BizProgram.query.filter(BizProgram.no.like('%' + no + '%'), BizProgram.name.like('%' + name + '%')).order_by(BizProgram.timestamp_loc).all()
        file_name = u'项目报表-all'
    else:
        page = session['program_current_page']
        per_page = current_app.config['ITEM_COUNT_PER_PAGE']
        pagination = BizProgram.query.filter(BizProgram.no.like('%' + no + '%'), BizProgram.name.like('%' + name + '%')).order_by(BizProgram.timestamp_loc).paginate(page, per_page)
        program_data = pagination.items
        file_name = u'项目报表-'+str(page)
    data = {
        '项目编号': [program.no for program in program_data],
        '项目名称': [program.name for program in program_data],
        'PR编号': [program.pr for program in program_data],
        '合同编号': [program.contract for program in program_data],
        '负责人': [program.owner.user_name for program in program_data],
        '项目状态': [program.status.state.display if program.status else '未维护' for program in program_data],
        '项目描述': [program.desc for program in program_data]
    }
    # 字典导出的问题在于列顺序是不固定的
    #return excel.make_response_from_dict(data, file_name=file_name, file_type='xlsx')
    # 采用列表导出即可
    array_data = [['项目编号', '项目名称', 'PR编号', '合同编号', '负责人', '项目状态', '项目描述']]
    for program in program_data:
        array_data.append([program.no, program.name, program.pr, program.contract, program.owner.user_name , program.status.state.display if program.status else '未维护', program.desc])
    return excel.make_response_from_array(array_data, file_name=file_name, file_type='xlsx')
@bp_report.route('/issue', methods=['GET', 'POST'])
@login_required
@log_record('查看ISSUE报表')
def issue():
    form = IssueSearchForm()
    # 剔除admin后的所有用户
    all_users = SysUser.query.filter(~SysUser.user_id.in_(['admin'])).order_by(SysUser.user_name).all()
    user_list = []
    for user in all_users:
        user_list.append((user.id, user.user_name))
    all_programs = BizProgram.query.order_by(BizProgram.name).all()
    program_list = [('0', '---请选择---')]
    for program in all_programs:
        program_list.append((program.id, program.name))
    form.program.choices = program_list
    form.category.choices = [('0', '---请选择---')] + get_options('D006')
    form.grade.choices = [('0', '---请选择---')] + get_options('D007')
    form.state.choices = [('0', '---请选择---')] + get_options('D008')
    form.charge.choices = [('0', '---请选择---')] + user_list
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        try:
            pro = session['issue_search_pro'] if session['issue_search_pro'] else '0'
            category = session['issue_search_cat'] if session['issue_search_cat'] else '0'
            grade = session['issue_search_gra'] if session['issue_search_gra'] else '0'
            state = session['issue_search_sta'] if session['issue_search_sta'] else '0'
            charge = session['issue_search_cha'] if session['issue_search_cha'] else '0'
        except KeyError:
            pro = '0'
            category = '0'
            grade = '0'
            state = '0'
            charge = '0'
        form.program.data = pro
        form.category.data = category
        form.grade.data = grade
        form.state.data = state
        form.charge.data = charge
    if request.method == 'POST':
        page = 1
        # 所属项目
        pro = form.program.data
        category = form.category.data
        grade = form.grade.data
        state = form.state.data
        charge = form.charge.data
        # 存储查询条件，执行导出
        session['issue_current_page'] = page
        session['issue_search_pro'] = pro
        session['issue_search_cat'] = category
        session['issue_search_gra'] = grade
        session['issue_search_sta'] = state
        session['issue_search_cha'] = charge
    # 使用集合存储查询条件执行查询
    conditions = set()
    # issue类别
    if category != '0':
        conditions.add(BizProgramIssue.category_id == category)
    # issue等级
    if grade != '0':
        conditions.add(BizProgramIssue.grade_id == grade)
    # issue状态
    if state != '0':
        conditions.add(BizProgramIssue.state_id == state)
    # issue担当
    if charge != '0':
        conditions.add(BizProgramIssue.handler_id == charge)
    # 某个项目的issue清单
    if pro != '0':
        program = BizProgram.query.get_or_404(pro)
        members = []
        for member in program.members:
            members.append((member.member_id, member.member.user_name))
        form.charge.choices = [('0', '---请选择---')] + members
        pagination = BizProgramIssue.query.with_parent(program).filter(*conditions).order_by(BizProgramIssue.timestamp_loc).paginate(page, per_page)
    else:
        form.charge.choices = [('0', '---请选择---')] + user_list
        pagination = BizProgramIssue.query.filter(*conditions).order_by(BizProgramIssue.program_id).paginate(page, per_page)
    issues = pagination.items
    return render_template('biz/report/issue/index.html', form=form, issues=issues, pagination=pagination)
@bp_report.route('/issue/excel/export/<int:sign>', methods=['GET'])
@login_required
@log_record('导出ISSUE报表')
def export_issue(sign):
    '''
    Program清单导出
    :param sign: 0:导出全部 1:导出当前页
    :return:
    '''
    excel.init_excel(current_app)
    '''
        print('Conditions : %s %s %s %s %s' %(session['issue_search_pro'],
        session['issue_search_cat'],
        session['issue_search_gra'],
        session['issue_search_sta'],
        session['issue_search_cha']))
    '''
    page = session['issue_current_page']
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    data_header = [['项目所属', '类别', '等级', '状态', '提出人', '处理人', '邀请完成日期']]
    data_body = []
    if session['issue_search_pro'] is None:
        print('进入页面后直接导出......')
        if sign == 0:
            issues = BizProgramIssue.query.order_by(BizProgramIssue.program_id).all()
        else:
            pagination = BizProgramIssue.query.order_by(BizProgramIssue.program_id).paginate(page, per_page)
            issues = pagination.items
    else:
        print('查询数据后进行导出......')
        # 所属项目
        pro = session['issue_search_pro']
        # 使用集合存储查询条件
        conditions = set()
        # issue类别
        if session['issue_search_cat'] != '0':
            conditions.add(BizProgramIssue.category_id == session['issue_search_cat'])
        # issue等级
        if session['issue_search_gra'] != '0':
            conditions.add(BizProgramIssue.grade_id == session['issue_search_gra'])
        # issue状态
        if session['issue_search_sta'] != '0':
            conditions.add(BizProgramIssue.state_id == session['issue_search_sta'])
        # issue担当
        if session['issue_search_cha'] != '0':
            conditions.add(BizProgramIssue.handler_id == session['issue_search_cha'])
        # 某个项目的issue清单
        if pro != '0':
            program = BizProgram.query.get_or_404(pro)
            if conditions:
                if sign == 0:
                    issues = BizProgramIssue.query.with_parent(program).filter(*conditions).order_by(BizProgramIssue.timestamp_loc).all()
                else:
                    pagination = BizProgramIssue.query.with_parent(program).filter(*conditions).order_by(BizProgramIssue.timestamp_loc).paginate(page, per_page)
                    issues = pagination.items
            else:
                if sign == 0:
                    issues = BizProgramIssue.query.with_parent(program).order_by(BizProgramIssue.timestamp_loc).all()
                else:
                    pagination = BizProgramIssue.query.with_parent(program).order_by(BizProgramIssue.timestamp_loc).paginate(page, per_page)
                    issues = pagination.items
        else:
            if sign == 0:
                issues = BizProgramIssue.query.filter(*conditions).order_by(BizProgramIssue.program_id).all()
            else:
                pagination = BizProgramIssue.query.filter(*conditions).order_by(BizProgramIssue.program_id).paginate(page, per_page)
                issues = pagination.items
    for issue in issues:
        data_body.append([issue.program.name, issue.category.display, issue.grade.display, issue.state.display, get_current_user(issue.operator_id).user_name, issue.handler.user_name, issue.ask_finish_dt])
    data = data_header + data_body
    file_name = u'项目报表-all' if sign == 0 else u'项目报表-' + str(page)
    return excel.make_response_from_array(data, file_name=file_name, file_type='xlsx')