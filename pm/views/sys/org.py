'''
系统部门信息管理
'''
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from pm.models import BizDept
from pm.plugins import db
from pm.forms.sys.org import OrgSearchForm, OrgForm
import uuid
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
    pagination = BizDept.query.filter(BizDept.code.like('%'+code+'%'), BizDept.name.like('%'+name+'%')).order_by(BizDept.code).paginate(page, per_page)
    orgs = pagination.items
    return render_template('sys/org/index.html', pagination=pagination, orgs=orgs, form=form)

@bp_org.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = OrgForm()
    departments = BizDept.query.order_by(BizDept.code).all()
    department_list = []
    for department in departments:
        department_list.append((department.id, department.name))
    form.parent.choices = department_list
    if form.validate_on_submit():
        department = BizDept(id=uuid.uuid4().hex, code=form.code.data.lower(), name=form.name.data, operator_id=current_user.id)
        db.session.add(department)
        db.session.commit()
        has_parent = form.has_parent.data
        if has_parent and form.parent.data is not None:
            department.set_parent_dept(BizDept.query.get(form.parent.data))
        flash('部门添加成功！')
        return redirect(url_for('.add'))
    return render_template('sys/org/add.html', form=form)