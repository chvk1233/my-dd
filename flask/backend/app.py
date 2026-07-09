import logging
import sys
from pathlib import Path

from flask import Flask
from flask_cors import CORS

import config
from routes.chat import chat_bp
from routes.events import events_bp
from routes.health import health_bp
from routes.ingest import ingest_bp
from routes.report import report_bp
from routes.tasks import tasks_bp
from services import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def create_app(db_path: str | None = None) -> Flask:
    if db_path:
        config.DATABASE_PATH = db_path

    app = Flask(__name__)
    CORS(app, origins=config.CORS_ORIGINS, supports_credentials=True)

    app.register_blueprint(health_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(ingest_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(chat_bp)

    db.init_db(config.DATABASE_PATH)
    return app


app = create_app()


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
