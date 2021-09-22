from flask import Blueprint, render_template, session
from flask_login import login_required
from pm.decorators import log_record
from pm.forms.biz.issue import IssueForm, IssueSearchForm
bp_issue = Blueprint('iss', __name__)
@bp_issue.route('/index', methods=['GET', 'POST'])
@login_required
@log_record('查看issue事项清单')
def index():
    form = IssueSearchForm()
    return render_template('biz/issue/index.html', form=form)
@bp_issue.route('/add', methods=['GET', 'POST'])
@login_required
@log_record('新增issue事项')
def add():
    form = IssueForm()
    return render_template('biz/issue/add.html', form=form)