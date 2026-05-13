from swimapp import create_app, db
from swimapp.models import User
from werkzeug.security import generate_password_hash
import os

app = create_app()

@app.route('/init-admin')
def init_admin():
    """Debug endpoint to reset admin credentials"""
    with app.app_context():
        # Delete existing admin
        User.query.filter_by(username='admin').delete()
        
        # Create fresh admin
        admin = User(
            username='admin',
            email=os.environ.get('ADMIN_EMAIL', 'admin@swimscore.local'),
            password_hash=generate_password_hash(os.environ.get('ADMIN_PASSWORD', 'Admin1234!')),
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        
        return f"Admin user created. Username: admin, Password: {os.environ.get('ADMIN_PASSWORD', 'Admin1234!')}"

if __name__ == '__main__':
    app.run(debug=True)
