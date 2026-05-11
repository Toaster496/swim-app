import random
import string
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from flask import (
    Blueprint, render_template, redirect, url_for,
    request, session, flash, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from . import db
from .models import User, AuditLog

auth_bp = Blueprint('auth', __name__)


def _log(action, severity='INFO', status='SUCCESS'):
    entry = AuditLog(
        ip_address=request.remote_addr,
        user_username=current_user.username if current_user.is_authenticated else 'anonymous',
        action_details=action,
        severity=severity,
        status=status
    )
    db.session.add(entry)
    db.session.commit()


def _send_otp(email, otp):
    mail_server = current_app.config.get('MAIL_SERVER', '')
    mail_user = current_app.config.get('MAIL_USERNAME', '')
    mail_pass = current_app.config.get('MAIL_PASSWORD', '')

    # if no mail config, just print to console - handy for local dev
    if not mail_server or not mail_user:
        print(f'\n[2FA] OTP for {email}: {otp}\n', flush=True)
        return True

    try:
        msg = MIMEText(
            f'Your Swim Score Pro login code is: {otp}\n\nThis code expires in 5 minutes.',
            'plain'
        )
        msg['Subject'] = 'Swim Score Pro - Login Code'
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = email

        with smtplib.SMTP(mail_server, current_app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(mail_user, mail_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f'[MAIL ERROR] Could not send OTP: {e}')
        # fall back to console so the user isn't completely locked out
        print(f'[2FA FALLBACK] OTP for {email}: {otp}')
        return False


@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            _log(f'Failed login for username: {username}', severity='WARN', status='DENIED')
            error = 'Invalid credentials or expired session.'
        elif not user.is_active:
            error = 'This account has been disabled.'
        else:
            # generate 6 digit OTP and store in session with expiry
            otp = ''.join(random.choices(string.digits, k=6))
            session['pending_user_id'] = user.id
            session['otp'] = otp
            session['otp_expires'] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()

            _send_otp(user.email, otp)
            return redirect(url_for('auth.verify_2fa'))

    return render_template('auth/login.html', error=error)


@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'pending_user_id' not in session:
        return redirect(url_for('auth.login'))

    error = None
    resent = request.args.get('resent')

    if request.method == 'POST':
        # collect the 6 individual digit inputs
        entered = ''.join([request.form.get(f'd{i}', '') for i in range(1, 7)])

        otp = session.get('otp', '')
        expires_str = session.get('otp_expires', '')

        expired = False
        if expires_str:
            expires = datetime.fromisoformat(expires_str)
            if datetime.utcnow() > expires:
                expired = True

        if expired:
            error = 'Code has expired. Please request a new one.'
        elif entered != otp:
            _log('Failed 2FA attempt', severity='WARN', status='DENIED')
            error = 'Incorrect code. Please try again.'
        else:
            user = User.query.get(session.pop('pending_user_id'))
            session.pop('otp', None)
            session.pop('otp_expires', None)
            login_user(user)
            _log('Successful login via 2FA', severity='INFO', status='SUCCESS')
            return redirect(url_for('admin.dashboard'))

    return render_template('auth/verify_2fa.html', error=error, resent=resent)


@auth_bp.route('/resend-otp')
def resend_otp():
    uid = session.get('pending_user_id')
    if not uid:
        return redirect(url_for('auth.login'))

    user = User.query.get(uid)
    otp = ''.join(random.choices(string.digits, k=6))
    session['otp'] = otp
    session['otp_expires'] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    _send_otp(user.email, otp)

    return redirect(url_for('auth.verify_2fa', resent=1))


@auth_bp.route('/logout')
@login_required
def logout():
    _log('User logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
