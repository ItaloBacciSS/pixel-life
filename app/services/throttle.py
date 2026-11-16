from datetime import datetime, timedelta, timezone

from ..extensions import db
from ..models import LoginFailure

MAX_FAILURES = 5  # erros de senha por usuário
MAX_FAILURES_IP = 20  # erros de senha por origem (cobre quem testa vários usuários)
WINDOW = timedelta(minutes=15)
MAX_SIGNUPS = 5  # contas novas por origem
SIGNUP_WINDOW = timedelta(hours=1)
KEEP = max(WINDOW, SIGNUP_WINDOW)


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def blocked(key, limit=MAX_FAILURES, window=WINDOW):
    recent = LoginFailure.query.filter(LoginFailure.username == key[:40], LoginFailure.at > now() - window)
    return recent.count() >= limit


def record(key):
    LoginFailure.query.filter(LoginFailure.at <= now() - KEEP).delete()
    db.session.add(LoginFailure(username=key[:40], at=now()))
    db.session.commit()


def clear(key):
    LoginFailure.query.filter_by(username=key[:40]).delete()
    db.session.commit()
