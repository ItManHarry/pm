from pm.plugins import scheduler, db
from pm.models import SysUser, SysLog
import uuid, time
def synch_job(a, b):
    # 使用上下文，否则报错
    with scheduler.app.app_context():
        app = scheduler.app
        log = SysLog(id=uuid.uuid4().hex, url='null', operation='Synchronize data', user_id='null', operator_id='null')
        db.session.add(log)
        db.session.commit()
        print('Config value is : ', app.config['SECRET_KEY'])
        print('Parameter a is %s b is %s' % (a, b))
        print('User total is : ', len(SysUser.query.all()))
def synch_print():
    # 使用上下文，否则报错
    with scheduler.app.app_context():
        print('Schedule task , execute time %s' %time.strftime('%Y-%m-%d %H:%M:%S'))
'''
    任务清单
'''
jobs = [
    # 每天下午两点5分执行一次
    {
        "id": "synch_user",
        "func": synch_job,
        "args": (1, 2),
        "trigger": "cron",
        "hour": 14,
        "minute": 5
    },
    # 每五分钟执行一次
    {
        "id": "synch_print",
        "func": synch_print,
        #"args": (),
        "trigger": "interval",
        "seconds": 300
    }
]