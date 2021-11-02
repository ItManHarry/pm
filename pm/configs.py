import os
dev_db = os.getenv('DEV_DB')
test_db = os.getenv('TEST_DB')
pro_db = os.getenv('PRO_DB')
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
class GlobalConfig():
    SECRET_KEY = os.getenv('SECRET_KEY', '123456789qazxswedcvfr!@#@452631')
    AD_JAR_PATH = os.path.join(basedir, 'ad')  # AD验证jar包路径
    ITEM_COUNT_PER_PAGE = 10
    FILE_UPLOAD_PATH = 'D:/Development/Python/workplaces/uploads'
    DROPZONE_MAX_FILE_SIZE = 3              # Dropzone上传文件大小(3M)
    DROPZONE_MAX_FILES = 5                  # Dropzone上传文件最大数量
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024    # Flask内置文件上传大小设置
    DROPZONE_ALLOWED_FILE_TYPE = 'image'    # Dropzone允许上传的文件类型
    DROPZONE_ENABLE_CSRF = True             # Dropzone上传启用CSRF令牌验证
    DROPZONE_IN_FORM = True                 # 嵌入表单
    DROPZONE_UPLOAD_ON_CLICK = True         # 点击选择文件
    # 以下为Dropzone错误消息提示
    DROPZONE_INVALID_FILE_TYPE = '上传文件类型错误！'
    DROPZONE_FILE_TOO_BIG = '上传文件超过最大限制！'
    DROPZONE_SERVER_ERROR = '服务端错误!'
    DROPZONE_BROWSER_UNSUPPORTED = '浏览器不支持！'
    DROPZONE_MAX_FILE_EXCEED = '超出最大文件上传数量！'
class DevelopConfig(GlobalConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DEVELOP_DATABASE_URL', dev_db)
    JVM_PATH = os.getenv('DEV_JVM_PATH', '')
class TestConfig(GlobalConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', test_db)
    JVM_PATH = os.getenv('TST_JVM_PATH', '')
    WTF_CSRF_ENABLED = False
    TESTING = True
class ProductConfig(GlobalConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('PRODUCT_DATABASE_URL', pro_db)
    JVM_PATH = os.getenv('PRO_JVM_PATH', '')
configurations = {
    'dev_config': DevelopConfig,
    'test_config': TestConfig,
    'pro_config': ProductConfig
}