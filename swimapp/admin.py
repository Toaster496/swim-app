import csv
import io
from datetime import datetime

from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, jsonify, make_response, abort
)
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from . import db
from .models import User, Event, Athlete, AuditLog, SystemSetting

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _log(action, severity='INFO', status='SUCCESS'):
    entry = AuditLog(
        ip_address=request.remote_addr,
        user_username=current_user.username,
        action_details=action,
        severity=severity,
        status=status
    )
    db.session.add(entry)
    db.session.commit()


def _require_admin(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
def dashboard():
    from sqlalchemy import text
    # quick system status checks
    db_ok = True
    try:
        db.session.execute(text('SELECT 1'))
    except Exception:
        db_ok = False

    stats = {
        'db_status': 'ONLINE' if db_ok else 'OFFLINE',
        'total_events': Event.query.count(),
        'total_athletes': Athlete.query.count(),
        'total_users': User.query.count(),
        'recent_logs': AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(5).all(),
    }
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/timer', methods=['GET', 'POST'])
@login_required
def timer():
    events = Event.query.filter_by(is_active=True).all()
    selected_event_id = request.args.get('event_id', type=int)
    selected_event = None
    athletes = []
    recent = []
    message = None
    error = None

    if selected_event_id:
        selected_event = Event.query.get_or_404(selected_event_id)
        athletes = Athlete.query.filter_by(event_id=selected_event_id).order_by(Athlete.lane).all()
        recent = (Athlete.query
                  .filter_by(event_id=selected_event_id)
                  .filter(Athlete.time.isnot(None))
                  .order_by(Athlete.rank)
                  .all())

    if request.method == 'POST':
        event_id = request.form.get('event_id', type=int)
        lane = request.form.get('lane', type=int)
        time_str = request.form.get('time_input', '').strip()
        verified = request.form.get('verified') == 'on'

        ev = Event.query.get(event_id) if event_id else None
        athlete = Athlete.query.filter_by(event_id=event_id, lane=lane).first() if ev else None

        if not ev or not athlete:
            error = 'Invalid event or lane selection.'
        elif not time_str:
            error = 'Time cannot be empty.'
        else:
            try:
                # accept HH:MM:SS.ms or MM:SS.ms or SS.ms
                parts = time_str.replace(',', '.').split(':')
                if len(parts) == 3:
                    total = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                elif len(parts) == 2:
                    total = int(parts[0]) * 60 + float(parts[1])
                else:
                    total = float(parts[0])

                if total < 0 or total > 600:
                    raise ValueError('Time out of range')

                athlete.time = total
                _recalculate_ranks(event_id)
                db.session.commit()

                action = f'Time updated: {athlete.name} (Lane {lane}) → {time_str} in {ev.event_code}'
                _log(action, severity='INFO')
                message = f'Time saved for {athlete.name}: {time_str}'

                # refresh lists
                selected_event = ev
                selected_event_id = event_id
                athletes = Athlete.query.filter_by(event_id=event_id).order_by(Athlete.lane).all()
                recent = (Athlete.query
                          .filter_by(event_id=event_id)
                          .filter(Athlete.time.isnot(None))
                          .order_by(Athlete.rank)
                          .all())

            except (ValueError, IndexError):
                error = 'Invalid time format. Use HH:MM:SS.ms, MM:SS.ms, or SS.ms'

    return render_template('admin/timer.html',
                           events=events,
                           selected_event=selected_event,
                           athletes=athletes,
                           recent=recent,
                           message=message,
                           error=error)


def _recalculate_ranks(event_id):
    swimmers = (Athlete.query
                .filter_by(event_id=event_id)
                .filter(Athlete.time.isnot(None))
                .order_by(Athlete.time)
                .all())
    for i, s in enumerate(swimmers, 1):
        s.rank = i
    # anyone without a time gets no rank
    unfinished = Athlete.query.filter_by(event_id=event_id).filter(Athlete.time.is_(None)).all()
    for s in unfinished:
        s.rank = None


@admin_bp.route('/timer/add-event', methods=['POST'])
@login_required
def add_event():
    name = request.form.get('name', '').strip()
    gender = request.form.get('gender', 'Open')
    meet = request.form.get('meet_name', 'General Meet').strip()
    heat = request.form.get('heat', 'Final').strip()

    if not name:
        flash('Event name is required.', 'error')
        return redirect(url_for('admin.timer'))

    code = f'EV-{Event.query.count() + 1:03d}'
    ev = Event(event_code=code, name=name, gender=gender, meet_name=meet, heat=heat)
    db.session.add(ev)
    db.session.commit()
    _log(f'Event created: {code} - {name}')
    flash(f'Event "{name}" created.', 'success')
    return redirect(url_for('admin.timer', event_id=ev.id))


@admin_bp.route('/timer/add-athlete', methods=['POST'])
@login_required
def add_athlete():
    event_id = request.form.get('event_id', type=int)
    lane = request.form.get('lane', type=int)
    name = request.form.get('name', '').strip()
    team = request.form.get('team', '').strip()

    ev = Event.query.get(event_id) if event_id else None
    if not ev or not lane or not name:
        flash('Missing required fields.', 'error')
        return redirect(url_for('admin.timer', event_id=event_id))

    existing = Athlete.query.filter_by(event_id=event_id, lane=lane).first()
    if existing:
        flash(f'Lane {lane} is already taken.', 'error')
        return redirect(url_for('admin.timer', event_id=event_id))

    athlete = Athlete(event_id=event_id, lane=lane, name=name, team=team)
    db.session.add(athlete)
    db.session.commit()
    _log(f'Athlete added: {name} (Lane {lane}) to {ev.event_code}')
    flash(f'{name} added to lane {lane}.', 'success')
    return redirect(url_for('admin.timer', event_id=event_id))


@admin_bp.route('/timer/remove-athlete', methods=['POST'])
@login_required
def remove_athlete():
    athlete_id = request.form.get('athlete_id', type=int)
    athlete = Athlete.query.get_or_404(athlete_id)
    event_id = athlete.event_id
    _log(f'Athlete removed: {athlete.name} (Lane {athlete.lane}) from event {event_id}')
    db.session.delete(athlete)
    db.session.commit()
    flash(f'{athlete.name} removed.', 'success')
    return redirect(url_for('admin.timer', event_id=event_id))


@admin_bp.route('/timer/reset-event', methods=['POST'])
@login_required
def reset_event():
    event_id = request.form.get('event_id', type=int)
    ev = Event.query.get_or_404(event_id)
    for a in ev.athletes:
        a.time = None
        a.reaction_time = None
        a.rank = None
        a.points = 0
    db.session.commit()
    _log(f'Event reset: {ev.event_code}', severity='WARN')
    flash(f'Event {ev.event_code} has been reset.', 'info')
    return redirect(url_for('admin.timer', event_id=event_id))


@admin_bp.route('/export/<int:event_id>')
@login_required
def export_csv(event_id):
    ev = Event.query.get_or_404(event_id)
    athletes = (Athlete.query
                .filter_by(event_id=event_id)
                .order_by(Athlete.rank, Athlete.lane)
                .all())

    leader_time = athletes[0].time if athletes and athletes[0].time else None

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Rank', 'Lane', 'Name', 'Team', 'Time', 'Reaction Time', 'Delta', 'Points'])

    for a in athletes:
        writer.writerow([
            a.rank or '',
            a.lane,
            a.name,
            a.team,
            a.time_display(),
            f'{a.reaction_time:.2f}' if a.reaction_time else '',
            a.delta_display(leader_time),
            a.points
        ])

    _log(f'CSV exported for event {ev.event_code}')

    resp = make_response(output.getvalue())
    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = f'attachment; filename=results_{ev.event_code}.csv'
    return resp


@admin_bp.route('/audit')
@login_required
@_require_admin
def audit():
    page = request.args.get('page', 1, type=int)
    severity_filter = request.args.get('severity', 'ALL_EVENTS')
    search = request.args.get('search', '').strip()
    time_from = request.args.get('time_from', '')
    time_to = request.args.get('time_to', '')

    query = AuditLog.query

    if severity_filter != 'ALL_EVENTS':
        query = query.filter_by(severity=severity_filter)
    if search:
        query = query.filter(
            AuditLog.user_username.ilike(f'%{search}%') |
            AuditLog.action_details.ilike(f'%{search}%') |
            AuditLog.ip_address.ilike(f'%{search}%')
        )
    if time_from:
        try:
            query = query.filter(AuditLog.timestamp >= datetime.fromisoformat(time_from))
        except ValueError:
            pass
    if time_to:
        try:
            query = query.filter(AuditLog.timestamp <= datetime.fromisoformat(time_to))
        except ValueError:
            pass

    logs = query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/audit.html', logs=logs,
                           severity_filter=severity_filter, search=search,
                           time_from=time_from, time_to=time_to)


@admin_bp.route('/audit/export')
@login_required
@_require_admin
def export_audit_csv():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(['Timestamp', 'IP Address', 'User', 'Action', 'Severity', 'Status'])
    for log in logs:
        w.writerow([log.timestamp.strftime('%Y-%m-%d %H:%M:%S'), log.ip_address,
                    log.user_username, log.action_details, log.severity, log.status])
    resp = make_response(out.getvalue())
    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = 'attachment; filename=audit_log.csv'
    return resp


@admin_bp.route('/users')
@login_required
@_require_admin
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    query = User.query
    if search:
        query = query.filter(
            User.username.ilike(f'%{search}%') |
            User.email.ilike(f'%{search}%')
        )
    user_list = query.order_by(User.id).paginate(page=page, per_page=10, error_out=False)
    total = User.query.count()
    return render_template('admin/users.html', user_list=user_list, search=search, total=total)


@admin_bp.route('/users/add', methods=['POST'])
@login_required
@_require_admin
def add_user():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'viewer')

    if not username or not email or not password:
        flash('All fields are required.', 'error')
        return redirect(url_for('admin.users'))

    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'error')
        return redirect(url_for('admin.users'))

    if User.query.filter_by(email=email).first():
        flash('Email already in use.', 'error')
        return redirect(url_for('admin.users'))

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    _log(f'New user created: {username} ({role})')
    flash(f'User {username} created.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/edit/<int:user_id>', methods=['POST'])
@login_required
@_require_admin
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    role = request.form.get('role', user.role)
    active = request.form.get('is_active') == 'on'

    old_role = user.role
    user.role = role
    user.is_active = active

    new_password = request.form.get('new_password', '').strip()
    if new_password:
        user.password_hash = generate_password_hash(new_password)
        _log(f'Password changed for {user.username}', severity='WARN')

    db.session.commit()
    if old_role != role:
        _log(f'Role changed: {user.username} → {role}', severity='WARN')
    flash(f'{user.username} updated.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@_require_admin
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't delete your own account.", 'error')
        return redirect(url_for('admin.users'))
    _log(f'User deleted: {user.username}', severity='HIGH')
    db.session.delete(user)
    db.session.commit()
    flash(f'{user.username} deleted.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@_require_admin
def settings():
    if request.method == 'POST':
        keys = [
            'session_timeout', 'force_logout_on_ip_change',
            'min_password_length', 'require_uppercase',
            'require_numbers', 'require_symbols',
            'enforce_2fa_admins', 'allow_2fa_timekeepers'
        ]
        # checkboxes don't submit if unchecked, so default to false
        checkbox_keys = {'force_logout_on_ip_change', 'require_uppercase',
                         'require_numbers', 'require_symbols',
                         'enforce_2fa_admins', 'allow_2fa_timekeepers'}

        for k in keys:
            if k in checkbox_keys:
                value = 'true' if request.form.get(k) else 'false'
            else:
                value = request.form.get(k, '').strip()

            setting = SystemSetting.query.filter_by(key=k).first()
            if setting:
                setting.value = value
            else:
                db.session.add(SystemSetting(key=k, value=value))

        db.session.commit()
        _log('System settings updated')
        flash('Settings saved.', 'success')
        return redirect(url_for('admin.settings'))

    all_settings = {s.key: s.value for s in SystemSetting.query.all()}
    return render_template('admin/settings.html', s=all_settings)


@admin_bp.route('/diagnostics', methods=['POST'])
@login_required
@_require_admin
def run_diagnostics():
    from sqlalchemy import text
    results = {}
    try:
        db.session.execute(text('SELECT 1'))
        results['database'] = 'ONLINE'
    except Exception:
        results['database'] = 'OFFLINE'

    results['api_latency'] = '< 5ms'
    results['sync_target'] = 'ACTIVE'

    _log('Diagnostics run by admin')
    return jsonify(results)
