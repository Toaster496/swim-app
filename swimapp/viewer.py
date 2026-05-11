from flask import Blueprint, render_template, request, jsonify
from .models import Event, Athlete

viewer_bp = Blueprint('viewer', __name__)


@viewer_bp.route('/live')
def live():
    events = Event.query.filter_by(is_active=True).all()
    selected_event_id = request.args.get('event_id', type=int)
    gender_filter = request.args.get('gender', '')
    meet_filter = request.args.get('meet', '')
    search = request.args.get('search', '').strip()

    selected_event = None
    athletes = []
    leader_time = None

    if selected_event_id:
        selected_event = Event.query.get(selected_event_id)
    elif events:
        selected_event = events[0]
        selected_event_id = events[0].id

    if selected_event:
        query = Athlete.query.filter_by(event_id=selected_event.id)
        if search:
            query = query.filter(
                Athlete.name.ilike(f'%{search}%') |
                Athlete.team.ilike(f'%{search}%')
            )
        athletes = query.order_by(Athlete.rank, Athlete.lane).all()
        finished = [a for a in athletes if a.time is not None]
        leader_time = finished[0].time if finished else None

    # get unique meets and genders for the dropdowns
    all_events = Event.query.filter_by(is_active=True).all()
    meets = sorted(set(e.meet_name for e in all_events))
    genders = sorted(set(e.gender for e in all_events))

    page = request.args.get('page', 1, type=int)
    per_page = 6
    total = len(athletes)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = athletes[start:end]
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return render_template('viewer/live.html',
                           events=events,
                           selected_event=selected_event,
                           athletes=paginated,
                           leader_time=leader_time,
                           meets=meets,
                           genders=genders,
                           meet_filter=meet_filter,
                           gender_filter=gender_filter,
                           search=search,
                           page=page,
                           total=total,
                           total_pages=total_pages,
                           per_page=per_page)


@viewer_bp.route('/scoreboard')
def scoreboard():
    selected_event_id = request.args.get('event_id', type=int)
    events = Event.query.filter_by(is_active=True).all()
    selected_event = None

    if selected_event_id:
        selected_event = Event.query.get(selected_event_id)
    elif events:
        selected_event = events[0]

    athletes = []
    if selected_event:
        athletes = (Athlete.query
                    .filter_by(event_id=selected_event.id)
                    .order_by(Athlete.rank, Athlete.lane)
                    .all())

    return render_template('viewer/scoreboard.html',
                           event=selected_event,
                           athletes=athletes,
                           events=events)


@viewer_bp.route('/api/live')
def api_live():
    event_id = request.args.get('event_id', type=int)
    if not event_id:
        events = Event.query.filter_by(is_active=True).first()
        if events:
            event_id = events.id
        else:
            return jsonify({'data': [], 'last_updated': 'No events'})

    athletes = (Athlete.query
                .filter_by(event_id=event_id)
                .order_by(Athlete.rank, Athlete.lane)
                .all())

    finished = [a for a in athletes if a.time is not None]
    leader_time = finished[0].time if finished else None

    from datetime import datetime
    return jsonify({
        'data': [a.to_dict(leader_time) for a in athletes],
        'last_updated': datetime.utcnow().strftime('%H:%M:%S UTC')
    })
