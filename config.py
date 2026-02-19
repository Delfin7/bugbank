import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bugbank-super-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'bugbank.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session timeout in seconds (5 minutes for testing timeout scenarios)
    PERMANENT_SESSION_LIFETIME = 300
    
    # Delays for AJAX simulation (in milliseconds)
    AJAX_MIN_DELAY = 500
    AJAX_MAX_DELAY = 2000
    
    # 2FA code for testing
    TWO_FACTOR_CODE = '123456'
    
    # Max failed login attempts before lock
    MAX_LOGIN_ATTEMPTS = 3


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
