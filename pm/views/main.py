from flask import Blueprint, render_template, session, jsonify
from flask_login import login_required, current_user
from pm.models import BizProgramStatus, BizProgramIssue, BizProgram
from pm.utils import get_options
bp_main = Blueprint('main', __name__)
@bp_main.route('/index')
@login_required
def index():
    # 清空session值
    session.pop('nav', None)
    session.pop('module_id', None)
    session.pop('menus', None)
    role = current_user.role
    return render_template('main/index.html')
'''
项目现况图表
'''
@bp_main.route('/charts/programs', methods=['POST'])
@login_required
def charts_programs():
    data = []
    options = get_options('D003')
    for option in options:
        state_list = BizProgramStatus.query.filter_by(state_id=option[0]).all()
        data.append({'value': len(state_list), 'name': option[1]})
    return jsonify(data=data)
'''
ISSUE处理现况图表
'''
@bp_main.route('/charts/issues', methods=['POST'])
@login_required
def charts_issues():
    programs = BizProgram.query.order_by(BizProgram.name).all()
    xdata = []
    ydata = []
    pro_ids = []
    for program in programs:
        xdata.append(program.name)
        pro_ids.append(program.id)
    options = get_options('D008')
    for option in options:
        item = {'name': option[1], 'type': 'bar'}
        counts = []
        for pro_id in pro_ids:
            counts.append(len(BizProgramIssue.query.filter(BizProgramIssue.program_id == pro_id, BizProgramIssue.state_id == option[0]).all()))
        item['data'] = counts
        ydata.append(item)
    data = {'xdata': xdata, 'ydata': ydata}
    return jsonify(data=data)