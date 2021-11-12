from pm.plugins import scheduler, db
from pm.models import SysUser, SysLog
import uuid

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