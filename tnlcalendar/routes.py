#!/usr/bin/env python3
import os
from datetime import datetime

import bleach
import markdown
from flask import current_app as app
from flask import render_template, abort, request, redirect, flash, url_for, send_from_directory, jsonify
from sqlalchemy import asc

from . import db
from .models import KalenderEvent
from .util import validate_form


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route('/calendar/events')
def calendar_events():
    if request.args.get('start') and request.args.get('end'):
        events = KalenderEvent.query.filter(KalenderEvent.start_date >= request.args.get('start')) \
            .filter(KalenderEvent.end_date <= request.args.get('end'))
    else:
        events = KalenderEvent.query.all()

    calender_dict = []

    for e in events:
        calender_dict.append({
            'title': e.title,
            'start': e.start_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': e.end_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'url': url_for('event', event_id=e.id)
        })

    return jsonify(calender_dict)


@app.route('/api/<token>/calendar/events')
def calendar_events_api(token):
    if token != 'sometokenyoudefinitelydidnthardcodeinhere':
        abort(401)

    if request.args.get('type') == 'first':
        e = KalenderEvent.query.filter(KalenderEvent.start_date >= datetime.now()).order_by(asc('start_date')).first_or_404()

        calender_dict = []

        calender_dict.append({
            'title': e.title,
            'start_date': e.start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': e.end_date.strftime('%Y-%m-%d %H:%M:%S'),
            'url': url_for('event', event_id=e.id),
            'nickname': e.nickname
        })

        return jsonify(calender_dict)
    # Maybe return everything by default instead
    return 'bleep bloop'


@app.route("/event/<event_id>", methods=["GET"])
def event(event_id):
    event = KalenderEvent.query.filter_by(id=event_id).first_or_404()

    allowed_tags = ['tbody', 'th', 'img', 'ins', 'mark', 'sup', 'dl', 'p', 'br', 'abbr', 'hr', 'strong', 'ul', 'li',
                    'ol', 'pre', 'code', 'thead', 'table', 'td', 'tr', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'em',
                    'blockquote', 'dt', 'dd', 'div']
    allowed_attr = {'*': ['class'],
                    'a': ['href', 'rel'],
                    'img': ['src', 'alt', 'width', 'height']}

    if event:
        # item.item = markdown.markdown(item.item, extensions=['extra', 'tables', 'nl2br'])
        event.event = bleach.clean(markdown.markdown(event.event, extensions=['extra', 'tables', 'nl2br']),
                                   tags=allowed_tags, attributes=allowed_attr)

    return render_template("event.html", event=event)


@app.route("/toevoegen", methods=["GET", "POST"])
def toevoegen():
    default_value = None

    start = request.args.get('start', None)
    end = request.args.get('end', None)

    if request.method == "POST":
        if not validate_form(request.form):
            return redirect(url_for('toevoegen'))

        nickname = request.form['nickname']
        titel = request.form['titel']
        event = request.form.get('event', default_value)
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')

        new_item = KalenderEvent(nickname=nickname,
                                 title=titel,
                                 event=event,
                                 start_date=start_date,
                                 end_date=end_date,
                                 time_created=datetime.now(),
                                 )

        db.session.add(new_item)
        db.session.commit()
        flash("Dank! Je event is toegevoegd", "success")
        return redirect(url_for('index'))

    now = datetime.now()
    return render_template("form.html",
                           start=start,
                           end=end,
                           start_date=now.strftime('%Y-%m-%dT%H:%M'))


@app.route("/aanpassen/<event_id>", methods=["GET", "POST"])
def aanpassen(event_id=None):
    delete = request.args.get('delete', False)

    event = KalenderEvent.query.filter_by(id=event_id).first_or_404()

    default_value = None

    if request.method == "POST":
        if not validate_form(request.form):
            print('form not validated')
            return redirect(url_for('aanpassen', event_id=event_id))

        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')

        event.nickname = request.form['nickname']
        event.title = request.form['titel']
        event.event = request.form.get('event', default_value)
        event.start_date = start_date
        event.end_date = end_date
        event.last_edit = datetime.now()

        try:
            db.session.commit()
            flash("Je event is aangepast!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
            abort(400)

    if delete:
        try:
            KalenderEvent.query.filter_by(id=event.id).delete()
            db.session.commit()
            flash("Je event is verwijderd!", "success")
            return redirect(url_for('index'))
        except:
            print(e)
            abort(400)

    return render_template("form.html",
                           event=event)


@app.errorhandler(404)
def page_not_found(e):
    flash(e, 'info')
    return redirect(url_for('index'))


@app.errorhandler(400)
def page_not_found(e):
    flash(e, 'info')
    return redirect(url_for('index'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')
