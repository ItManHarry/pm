from pm.plugins import scheduler
from pm.models import SysUser

def synch_job():
    with scheduler.app.app_context():
        print('User total is : ', len(SysUser.query.all()))