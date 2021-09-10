'''
系统字典信息管理
'''
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from pm.models import SysDict, SysEnum
from pm.plugins import db
from pm.forms.sys.dicts import DictForm, DictSearchForm
from pm.decorators import log_record
import uuid
bp_dict = Blueprint('dict', __name__)
@bp_dict.route('/index', methods=['GET', 'POST'])
@login_required
@log_record('查询系统字典清单')
def index():
    code = ''
    name = ''
    form = DictSearchForm()
    if request.method == 'POST':
        code = form.code.data
        name = form.name.data
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEM_COUNT_PER_PAGE']
    pagination = SysDict.query.filter(SysDict.code.like('%'+code+'%'), SysDict.name.like('%'+name+'%')).order_by(SysDict.code).paginate(page, per_page)
    dictionaries = pagination.items
    return render_template('sys/dict/index.html', pagination=pagination, dictionaries=dictionaries, form=form)

@bp_dict.route('/add', methods=['GET', 'POST'])
@login_required
@log_record('新增字典信息')
def add():
    form = DictForm()
    if form.validate_on_submit():
        dictionary = SysDict(id=uuid.uuid4().hex, code=form.code.data.upper(), name=form.name.data, operator_id=current_user.id)
        db.session.add(dictionary)
        db.session.commit()
        flash('字典信息添加成功！')
        return redirect(url_for('.add'))
    return render_template('sys/dict/add.html', form=form)
@bp_dict.route('/eidt/<id>', methods=['GET', 'POST'])
@login_required
@log_record('修改字典信息')
def edit(id):
    form = DictForm()
    dictionary = SysDict.query.get_or_404(id)    
    if request.method == 'GET':
        form.id.data = dictionary.id
        form.code.data = dictionary.code
        form.name.data = dictionary.name
    if form.validate_on_submit():
        dictionary.code = form.code.data
        dictionary.name = form.name.data
        dictionary.operator_id = current_user.id
        db.session.commit()
        flash('字典信息更新成功！')
        return redirect(url_for('.edit', id=form.id.data))
    return render_template('sys/dict/edit.html', form=form)
@bp_dict.route('/enums/<dict_id>', methods=['POST'])
@login_required
@log_record('获取字典枚举信息')
def enums(dict_id):
    dictionary = SysDict.query.get_or_404(dict_id)
    enums = []
    for enum in dictionary.enums:
        enums.append((enum.id, enum.display, enum.key if enum.key else ''))
    return jsonify(enums=enums)
@bp_dict.route('/enum_add', methods=['POST'])
@login_required
@log_record('修改字典枚举信息')
def enum_add():
    data = request.get_json()
    dict_id = data['dict_id']
    dictionary = SysDict.query.get_or_404(dict_id)
    # 先移除已关联的枚举值
    for enum in dictionary.enums:
        dictionary.enums.remove(enum)
        db.session.commit()
    # 移除的枚举执行删除
    removed = data['removed']
    print('Removed : ', removed)
    for enum_id in removed:
        enum = SysEnum.query.get(enum_id)
        if enum:
            db.session.delete(enum)
            db.session.commit()
    # 关联枚举值
    enums = data['p_enums']
    for enum in enums:
        print('Enum id : ', enum['id'], ', key : ', enum['key'], ', display : ', enum['display'])
        enumeration = SysEnum.query.get(str(enum['id']))
        if enumeration:
            enumeration.key = enum['key']
            enumeration.display = enum['display']
            enumeration.operator_id = current_user.id
            db.session.commit()
        else:
            enumeration = SysEnum(id=uuid.uuid4().hex, key=enum['key'], display=enum['display'], operator_id=current_user.id)
            db.session.add(enumeration)
            db.session.commit()
        dictionary.enums.append(enumeration)
        db.session.commit()
    return jsonify(code=1, message='枚举维护成功!')