from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class CustomAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    nome = db.Column(db.String(60), nullable=False)
    efeitos = db.Column(db.JSON, nullable=False)
    tropeco = db.Column(db.Boolean, nullable=False, default=False)


class Entry(db.Model):
    __table_args__ = (db.UniqueConstraint("user_id", "action_key", "day"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    action_key = db.Column(db.String(40), nullable=False)
    day = db.Column(db.Date, nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Character(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    corpo = db.Column(db.String(10), nullable=False)
    pele = db.Column(db.String(7), nullable=False)
    cabelo = db.Column(db.String(7), nullable=False)
    roupa = db.Column(db.String(7), nullable=False)
    itens = db.Column(db.JSON, nullable=False, default=list)


class Goal(db.Model):
    __table_args__ = (db.UniqueConstraint("user_id", "action_key"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    action_key = db.Column(db.String(40), nullable=False)
    vezes = db.Column(db.Integer, nullable=False)


class MoneyMove(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    day = db.Column(db.Date, nullable=False)
    cents = db.Column(db.BigInteger, nullable=False)
    note = db.Column(db.String(100))


class Home(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    tema = db.Column(db.String(20), nullable=False)
    especie = db.Column(db.String(20), nullable=False)
    pelagem = db.Column(db.String(20), nullable=False)


class LoginFailure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False, index=True)
    at = db.Column(db.DateTime, nullable=False)
