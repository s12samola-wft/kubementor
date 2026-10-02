import pytest

from app import create_app
from app.config import ProductionConfig


def test_unknown_environment_is_rejected():
    with pytest.raises(RuntimeError):
        create_app("staging")


def test_production_without_secret_key_is_rejected(monkeypatch):
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", None)

    with pytest.raises(RuntimeError):
        create_app("production")


def test_testing_config_is_loaded():
    app = create_app("testing")

    assert app.config["TESTING"] is True
    assert app.config["APP_ENV"] == "testing"

def test_production_with_secret_key_starts(monkeypatch):
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "drill-secret")
    app = create_app("production")

    assert app.config["SECRET_KEY"] == "drill-secret" 
      
