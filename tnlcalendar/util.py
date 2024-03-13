from datetime import datetime
from flask import flash, request


def validate_form(form):
    if form['start_date'] is None or form['start_date'] == '' or form['end_date'] is None or form['end_date'] == '':
        flash("Voeg een start of einddatum toe", "warning")
        print('no date')
        return False
    elif datetime.strptime(form['start_date'], '%Y-%m-%dT%H:%M') < datetime.now():
        flash("Startdata mogen niet in het verleden liggen", "warning")
        print('date in past')
        return False
    elif form['end_date'] < form['start_date'] or form['end_date'] == form['start_date']:
        flash("De einddatum mag niet eerder of gelijk zijn aan de startdatum", "warning")
        print('end date before start date')
        return False
    elif form['start_date'] and form['end_date']:
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')
        delta = end_date - start_date
        if delta.days > 5:
            print('event too long')
            flash("Events mogen niet langer dan 3 dagen duren in deze kalender, sorry!", "warning")
            return False

    return True
