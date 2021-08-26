'''
系统部门信息管理
'''
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required
from pm.models import BizDept
from pm.forms.sys.org import OrgSearchForm, OrgForm
bp_org = Blueprint('org', __name__)
@bp_org.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    code = ''
    name = ''
    form = OrgSearchForm()
    if request.method == 'POST':
        code = form.code.data
        name = form.name.data
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    pagination = BizDept.query.filter(BizDept.code.like('%'+code+'%'), BizDept.name.like('%'+name+'%')).order_by(BizDept.code.desc()).paginate(page, per_page)
    orgs = pagination.items
    return render_template('sys/org/index.html', pagination=pagination, orgs=orgs, form=form)

@bp_org.route('/add', methods=['GET', 'POST'])
def add():
    form = OrgForm()
    if form.validate_on_submit():
        flash('部门添加成功！')
        return redirect(url_for('.add'))
    return render_template('sys/org/add.html', form=form)