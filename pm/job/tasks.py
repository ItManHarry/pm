from pm.plugins import scheduler
from pm.models import SysUser

def synch_job():
    # 使用上下文，否则报错
    with scheduler.app.app_context():
        print('User total is : ', len(SysUser.query.all()))