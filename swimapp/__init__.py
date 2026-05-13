import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///swim.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # mail stuff - set in .env for real email. if not set, OTPs just print to console
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', '')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@swimscore.local')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to continue.'

    from .models import User

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(int(uid))

    from .auth import auth_bp
    from .admin import admin_bp
    from .viewer import viewer_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(viewer_bp)

    with app.app_context():
        db.create_all()
        _seed_defaults()

    # Debug route to reset admin password - REMOVE AFTER USE
    @app.route('/reset-admin')
    def reset_admin():
        from .models import User
        from werkzeug.security import generate_password_hash
        
        admin = User.query.filter_by(username='admin').first()
        if admin:
            new_pass = os.environ.get('ADMIN_PASSWORD', 'Admin1234!')
            admin.password_hash = generate_password_hash(new_pass)
            admin.email = os.environ.get('ADMIN_EMAIL', 'admin@swimscore.local')
            admin.is_active = True
            db.session.commit()
            return f'Admin reset. Username: admin, Password: {new_pass}<br>Check logs for OTP after login.'
        return 'Admin user not found'

    return app


def _seed_defaults():
    from .models import User, SystemSetting
    from werkzeug.security import generate_password_hash

    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email=os.environ.get('ADMIN_EMAIL', 'admin@swimscore.local'),
            password_hash=generate_password_hash(os.environ.get('ADMIN_PASSWORD', 'Admin1234!')),
            role='admin',
            is_active=True
        )
        db.session.add(admin)

    defaults = {
        'session_timeout': '30',
        'force_logout_on_ip_change': 'false',
        'min_password_length': '12',
        'require_uppercase': 'true',
        'require_numbers': 'true',
        'require_symbols': 'true',
        'enforce_2fa_admins': 'true',
        'allow_2fa_timekeepers': 'false',
    }
    for k, v in defaults.items():
        if not SystemSetting.query.filter_by(key=k).first():
            db.session.add(SystemSetting(key=k, value=v))

    db.session.commit()
