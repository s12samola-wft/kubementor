from flask import Blueprint

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return "Welcome to KubeMentor"


@main_bp.route("/health")
def health():
    return {"status": "healthy"}, 200


@main_bp.route("/ready")
def ready():
    return {"status": "ready"}, 200
