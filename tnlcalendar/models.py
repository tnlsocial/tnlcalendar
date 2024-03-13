#!/usr/bin/env python3
from . import db

class KalenderEvent(db.Model):
    __tablename__ = "KalenderEvent"
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    event = db.Column(db.String(500))
    time_created = db.Column(db.DateTime, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    last_edit = db.Column(db.DateTime, index=False)
