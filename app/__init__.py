import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from app.db.session import db
from app.routes.ui import ui_bp

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_secret_key")
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./local.db")
    if db_url.startswith("sqlite:///./") or db_url == "sqlite:///local.db":
        # Create an absolute path for sqlite
        db_path = Path(__file__).parent.parent / "local.db"
        db_path_resolved = db_path.resolve()
        db_url = (
            f"sqlite:///{db_path_resolved}"
            if sys.platform == "win32"
            else f"sqlite:////{db_path_resolved}"
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init DB
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(ui_bp)

    return app
