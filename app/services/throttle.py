from datetime import datetime, timedelta, timezone

from ..extensions import db
from ..models import LoginFailure

MAX_FAILURES = 5
WINDOW = timedelta(minutes=15)


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _recent(username):
    return LoginFailure.query.filter(
        LoginFailure.username == username, LoginFailure.at > now() - WINDOW
    )


def blocked(username):
    return _recent(username[:40]).count() >= MAX_FAILURES


def record_failure(username):
    LoginFailure.query.filter(LoginFailure.at <= now() - WINDOW).delete()
    db.session.add(LoginFailure(username=username[:40], at=now()))
    db.session.commit()


def clear(username):
    LoginFailure.query.filter_by(username=username[:40]).delete()
    db.session.commit()
