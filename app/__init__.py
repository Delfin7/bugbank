"""
BugBank Flask Application Factory
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Zaloguj się, aby uzyskać dostęp do tej strony.'
login_manager.login_message_category = 'warning'


def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.accounts import accounts_bp
    from app.routes.transfers import transfers_bp
    from app.routes.cards import cards_bp
    from app.routes.messages import messages_bp
    from app.routes.settings import settings_bp
    from app.routes.regulations import regulations_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(transfers_bp)
    app.register_blueprint(cards_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(regulations_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # User loader for Flask-Login
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Context processor for templates
    @app.context_processor
    def utility_processor():
        import random
        import string
        
        def generate_random_id(prefix='el'):
            """Generate random ID suffix for dynamic elements"""
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            return f"{prefix}_{suffix}"
        
        def random_delay():
            """Generate random delay for AJAX simulation"""
            return random.randint(
                app.config.get('AJAX_MIN_DELAY', 500),
                app.config.get('AJAX_MAX_DELAY', 2000)
            )
        
        return dict(
            generate_random_id=generate_random_id,
            random_delay=random_delay
        )
    
    return app
