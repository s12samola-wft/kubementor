import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    APP_ENV = os.getenv("APP_ENV", "development")


class DevelopmentConfig(Config):
    DEBUG = True
    APP_ENV = "development"


class TestingConfig(Config):
    TESTING = True
    APP_ENV = "testing"
    SECRET_KEY = os.getenv("TEST_SECRET_KEY", "test-only-secret-key")


class ProductionConfig(Config):
    DEBUG = False
    APP_ENV = "production"
