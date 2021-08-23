import os
dev_db = os.getenv('DEV_DB')
test_db = os.getenv('TEST_DB')
pro_db = os.getenv('PRO_DB')
class GlobalConfig():
    SECRET_KEY = os.getenv('SECRET_KEY', '123456789qazxswedcvfr!@#@452631')
class DevelopConfig(GlobalConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DEVELOP_DATABASE_URL', dev_db)
class TestConfig(GlobalConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', test_db)
    WTF_CSRF_ENABLED = False
    TESTING = True
class ProductConfig(GlobalConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('PRODUCT_DATABASE_URL', pro_db)
configurations = {
    'dev_config': DevelopConfig,
    'test_config': TestConfig,
    'pro_config': ProductConfig
}