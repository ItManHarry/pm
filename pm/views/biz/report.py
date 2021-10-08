from flask import Blueprint, current_app, render_template, url_for, request, session
from flask_login import login_required, current_user
from pm.models import BizProgram
from pm.forms.biz.program import ProgramSearchForm
from pm.decorators import log_record
import flask_excel as excel
bp_report = Blueprint('rpt', __name__)
@bp_report.route('/program', methods=['GET', 'POST'])
@login_required
@log_record('查看项目报表')
def program():
    no = ''  # 项目编号
    name = ''  # 项目名称
    form = ProgramSearchForm()
    if request.method == 'POST':
        no = form.no.data
        name = form.name.data
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    pagination = BizProgram.query.filter(BizProgram.no.like('%' + no + '%'), BizProgram.name.like('%' + name + '%')).order_by(BizProgram.timestamp_loc).paginate(page, per_page)
    programs = pagination.items
    # 供导出使用
    session['program_search_no'] = no
    session['program_search_nm'] = name
    session['program_current_page'] = page
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
    return excel.make_response_from_dict(data, file_name=file_name, file_type='xlsx')
@bp_report.route('/issue', methods=['GET', 'POST'])
@login_required
@log_record('查看ISSUE报表')
def issue():
    return render_template('biz/report/issue/index.html')
