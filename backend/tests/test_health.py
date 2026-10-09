def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready_checks_database(client):
    assert client.get("/ready").json() == {"status": "READY"}


def test_metrics_endpoint_is_prometheus_format(client):
    client.get("/health")
    body = client.get("/metrics").text
    assert "http_requests_total" in body
