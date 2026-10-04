def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_ready(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ready"}


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Welcome to KubeMentor"
