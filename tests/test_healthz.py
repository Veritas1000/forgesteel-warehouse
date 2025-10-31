def test_healthz(client):
    response = client.get('/healthz')
    assert b"version" in response.data