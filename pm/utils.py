'''
    系统工具函数
'''
import time, datetime, os, uuid
from flask import request, redirect, url_for
from urllib.parse import urlparse, urljoin
from pm.models import SysUser
#utc时间转本地
def utc_to_locale(utc_date):
    now_stamp = time.time()
    locale_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = locale_time - utc_time
    locale_date = utc_date + offset
    return locale_date
#获取当前时间
def get_time():
    return 'Now is : %s' %time.strftime('%Y年%m月%d日')
# 获取日期
def get_date():
    return time.strftime('%Y%m%d')
#格式化日期
def format_time(timestamp):
    return utc_to_locale(timestamp).strftime('%Y-%m-%d %H:%M:%S')
#判断地址是否安全
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http','https') and ref_url.netloc == test_url.netloc
'''
    通用返回方法
    默认返回博客首页
'''
def redirect_back(default='main.index', **kwargs):
    target = request.args.get('next')
    if target and is_safe_url(target):
        return redirect(target)
    return redirect(url_for(default, **kwargs))
'''
    重命名文件
'''
def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_file_name = uuid.uuid4().hex + ext
    return new_file_name
'''
根据字典代码获取枚举下拉值
'''
def get_options(code):
    from pm.models import SysDict
    dictionary = SysDict.query.filter_by(code=code).first()
    enums = dictionary.enums
    options = []
    for enum in enums:
        options.append((enum.id, enum.display))
    return options
'''
获取当前用户
'''
def get_current_user(id):
    return SysUser.query.get(id)