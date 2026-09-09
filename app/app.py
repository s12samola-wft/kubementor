from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Welcome to KubeMentor"


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


@app.route("/ready")
def ready():
    return {"status": "ready"}, 200
