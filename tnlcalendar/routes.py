#!/usr/bin/env python3
import os
from datetime import datetime

import bleach
import markdown
from flask import current_app as app
from flask import render_template, abort, request, redirect, flash, url_for, send_from_directory, session, jsonify
from sqlalchemy import asc

from . import db
from .auth import refrein
from .models import KalenderEvent
from .util import validate_form


@app.route("/", methods=["GET"])
def index():
    current_url = request.url.replace('http://', 'https://', 1)
    auth = request.args.get('auth', None)

    if auth:
        if not refrein(auth):
            return render_template('failure.html', msg="Your auth token did not verify"), 401

    try:
        cookie = session['name']
    except:
        cookie = False

    if not cookie:
        return render_template('auth.html', current_url=current_url), 401

    return render_template("index.html")


@app.route('/calendar/events')
def calendar_events():
    try:
        cookie = session['name']
    except:
        abort(401)

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
    return 'bleep bloop'


@app.route("/event/<event_id>", methods=["GET"])
def event(event_id):
    current_url = request.url.replace('http://', 'https://', 1)
    auth = request.args.get('auth', None)

    if auth:
        if not refrein(auth):
            return render_template('failure.html', msg="Your auth token did not verify"), 401

    try:
        cookie = session['name']
    except:
        cookie = False

    if not cookie:
        return render_template('auth.html', current_url=current_url), 401

    event = KalenderEvent.query.filter_by(id=event_id).first_or_404()

    authenticated = False

    if cookie == event.nickname:
        authenticated = True

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

    return render_template("event.html", event=event, authenticated=authenticated)


@app.route("/toevoegen", methods=["GET", "POST"])
def toevoegen():
    current_url = request.url.replace('http://', 'https://', 1)
    auth = request.args.get('auth', None)

    if auth:
        if not refrein(auth):
            return render_template('failure.html', msg="Your auth token did not verify"), 401

    try:
        cookie = session['name']
    except:
        cookie = False

    if not cookie:
        return render_template('auth.html', current_url=current_url), 401

    nickname = cookie
    default_value = None

    start = request.args.get('start', None)
    end = request.args.get('end', None)

    if request.method == "POST":
        if not validate_form(request.form):
            return redirect(url_for('toevoegen'))

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

        print('adding to db')
        db.session.add(new_item)
        db.session.commit()
        flash("Dank! Je event is toegevoegd", "success")
        return redirect(url_for('index'))

    now = datetime.now()
    return render_template("form.html",
                           nickname=nickname,
                           start=start,
                           end=end,
                           start_date=now.strftime('%Y-%m-%dT%H:%M'))


@app.route("/aanpassen/<event_id>", methods=["GET", "POST"])
def aanpassen(event_id=None):
    current_url = request.url.replace('http://', 'https://', 1)
    auth = request.args.get('auth', None)
    delete = request.args.get('delete', False)
    if auth:
        if not refrein(auth):
            return render_template('failure.html', msg="Your auth token did not verify"), 401

    try:
        cookie = session['name']
    except:
        cookie = False

    if not cookie:
        return render_template('auth.html', current_url=current_url), 401

    nickname = cookie

    event = KalenderEvent.query.filter_by(id=event_id).first_or_404()

    if event.nickname != nickname:
        flash("Dit event is niet van jou, helaas!", "warning")
        return redirect(url_for('index'))

    default_value = None

    if request.method == "POST":
        if not validate_form(request.form):
            print('form not validated')
            return redirect(url_for('aanpassen', event_id=event_id))

        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')

        event.title = request.form['titel']
        event.event = request.form.get('event', default_value)
        event.start_date = start_date
        event.end_date = end_date
        event.last_edit = datetime.now()

        try:
            print('adding to db')
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
                           nickname=nickname,
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
