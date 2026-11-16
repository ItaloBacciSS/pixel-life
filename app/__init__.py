from flask import Flask, jsonify

from .config import Config
from .errors import ApiError
from .extensions import db
from .migrations import add_missing_columns
from .security import init_security


def create_app(config=Config):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config)
    app.json.sort_keys = False  # mantém a ordem das regras no JSON
    db.init_app(app)

    from . import models  # noqa: F401  (registra as tabelas)
    from .routes import api, auth, character, game, goals, health, legal, profile, room, summary, wealth

    for module in (auth, game, api, character, profile, room, summary, goals, wealth, health, legal):
        app.register_blueprint(module.bp)

    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify(erro=str(error)), error.status

    @app.errorhandler(401)
    def handle_unauthorized(_):
        return jsonify(erro="Faça login para continuar."), 401

    init_security(app)

    with app.app_context():
        db.create_all()
        add_missing_columns()
    return app
