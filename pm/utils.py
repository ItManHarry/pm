'''
    系统工具函数
'''
import time, datetime, os, uuid
from flask import request, redirect, url_for
from flask_login import current_user
from urllib.parse import urlparse, urljoin
from pm.models import SysUser
def utc_to_locale(utc_date):
    '''
    utc时间转本地
    :param utc_date:
    :return:
    '''
    now_stamp = time.time()
    locale_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = locale_time - utc_time
    locale_date = utc_date + offset
    return locale_date
def get_time():
    '''
    获取当前时间
    :return:
    '''
    return 'Now is : %s' %time.strftime('%Y年%m月%d日')
def get_date():
    '''
    获取日期
    :return:
    '''
    return time.strftime('%Y%m%d')
def format_time(timestamp):
    '''
    格式化日期
    :param timestamp:
    :return:
    '''
    return utc_to_locale(timestamp).strftime('%Y-%m-%d %H:%M:%S')
def is_safe_url(target):
    '''
    判断地址是否安全
    :param target:
    :return:
    '''
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http','https') and ref_url.netloc == test_url.netloc
def redirect_back(default='main.index', **kwargs):
    '''
    通用返回方法(默认返回博客首页)
    :param default:
    :param kwargs:
    :return:
    '''
    target = request.args.get('next')
    if target and is_safe_url(target):
        return redirect(target)
    return redirect(url_for(default, **kwargs))
def random_filename(filename):
    '''
    重命名文件
    :param filename:
    :return:
    '''
    ext = os.path.splitext(filename)[1]
    new_file_name = uuid.uuid4().hex + ext
    return new_file_name
def get_options(code):
    '''
    根据字典代码获取枚举下拉值
    :param code:
    :return:
    '''
    from pm.models import SysDict
    dictionary = SysDict.query.filter_by(code=code).first()
    enums = dictionary.enums
    options = []
    for enum in enums:
        options.append((enum.id, enum.display))
    return options
def get_current_user(id):
    '''
    获取当前用户
    :param id:
    :return:
    '''
    return SysUser.query.get(id)