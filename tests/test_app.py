from app import create_app


def test_health_endpoint():
    app = create_app()
    client = app.test_client()

    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_year_from_age_valid():
    app = create_app()
    client = app.test_client()

    response = client.get("/year?age=10")
    data = response.get_json()

    assert response.status_code == 200
    assert data["age"] == 10
    assert data["nc_year"] == 6  # 10 - 4
