import os

from flask import Flask

from app.config import DevelopmentConfig, ProductionConfig, TestingConfig


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv("APP_ENV", "development")

    configs = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }

    config_class = configs.get(config_name)

    if config_class is None:
        raise RuntimeError(f"Unknown application environment: {config_name}")

    app.config.from_object(config_class)

    if config_name == "production" and not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be provided in production")

    from app.routes.main import main_bp

    app.register_blueprint(main_bp)

    return app
