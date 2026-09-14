from app import create_app

def test_health():
    app = create_app("testing")
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}
def test_ready():
    app = create_app()
    client = app.test_client()
    
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ready"}
def test_home():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Welcome to KubeMentor"    
