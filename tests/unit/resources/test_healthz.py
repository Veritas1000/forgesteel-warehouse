from flask import json
import re

def test_healthz_returns_version(client):
    response = client.get('/healthz')
    data = json.loads(response.data)
    assert "version" in data.keys(), '"version" should be present in response'
    version = data['version']
    assert re.match(r"\d+\.\d+\.\d+", version), f"{version} not in the form x.y.z"
