def test_get_homebrew_succeeds(clean_data_client, user_headers):
    response = clean_data_client.get("/data/forgesteel-homebrew-settings", headers=user_headers)

    assert response.status_code == 200
    assert response.json is not None
    assert "data" in response.json

def test_get_unknown_homebrew_404s(clean_data_client, user_headers):
    ## No homebrew object
    response = clean_data_client.get("/data/forgesteel-homebrew-settings/unknown", headers=user_headers)
    assert response.status_code == 404

    response = clean_data_client.put(
        "/data/forgesteel-homebrew-settings/123",
        json={"id": "123", "foo": "bar"},
        headers=user_headers,
    )
    assert response.status_code == 204

    ## No homebrew with ID
    response = clean_data_client.get("/data/forgesteel-homebrew-settings/222", headers=user_headers)
    assert response.status_code == 404

def test_put_homebrew_succeeds(clean_data_client, user_headers):
    response = clean_data_client.put("/data/forgesteel-homebrew-settings/123",
                          json={"id": "123", "foo": "bar"},
                          headers=user_headers)

    assert response.status_code == 204


def test_put_homebrew_no_id_fails(clean_data_client, user_headers):
    response = clean_data_client.put(
        "/data/forgesteel-homebrew-settings/666",
        json={"foo": "bar"},
        headers=user_headers,
    )
    assert response.status_code == 400


def test_put_homebrew_mismatch_id_fails(clean_data_client, user_headers):
    response = clean_data_client.put(
        "/data/forgesteel-homebrew-settings/666",
        json={"id": "123", "foo": "bar"},
        headers=user_headers,
    )

    assert response.status_code == 400


def test_get_homebrew_returns_same_as_put(clean_data_client, user_headers):
    homebrew_data = {"id": "234", "foo": "baz"}
    endpoint = "/data/forgesteel-homebrew-settings/234"
    response = clean_data_client.put(
        endpoint,
        json=homebrew_data,
        headers=user_headers,
    )

    assert response.status_code == 204

    response2 = clean_data_client.get(endpoint, headers=user_headers)

    assert response2.status_code == 200
    assert response2.json["data"] == homebrew_data


def test_put_homebrew_updates_existing(clean_data_client, user_headers):
    homebrew_id = "345"
    homebrew_data = {"id": homebrew_id, "foo": "baz"}
    endpoint = f"/data/forgesteel-homebrew-settings/{homebrew_id}"
    response1 = clean_data_client.put(
        endpoint,
        json=homebrew_data,
        headers=user_headers,
    )

    assert response1.status_code == 204

    response2 = clean_data_client.get(endpoint, headers=user_headers)

    assert response2.status_code == 200
    assert response2.json["data"] == homebrew_data

    homebrew_data2 = {"id": homebrew_id, "foo": "bam", "name": "FooBar"}
    response3 = clean_data_client.put(
        endpoint,
        json=homebrew_data2,
        headers=user_headers,
    )

    assert response3.status_code == 204

    response4 = clean_data_client.get(endpoint, headers=user_headers)
    assert response4.status_code == 200
    assert response4.json["data"] == homebrew_data2


def test_put_single_homebrew_returned_with_full_list(clean_data_client, user_headers):
    homebrew_id = "456"
    homebrew_data = {"id": homebrew_id, "foo": "baz"}
    endpoint = f"/data/forgesteel-homebrew-settings/{homebrew_id}"
    response1 = clean_data_client.put(
        endpoint,
        json=homebrew_data,
        headers=user_headers,
    )

    assert response1.status_code == 204

    response2 = clean_data_client.get(
        "/data/forgesteel-homebrew-settings", headers=user_headers
    )
    assert response2.status_code == 200
    homebrews_list = response2.json["data"]
    assert len(homebrews_list) == 1
    assert homebrews_list[0] == homebrew_data


def test_delete_homebrew_404s_on_nonexistent(clean_data_client, user_headers):
    ## no homebrewes object
    response = clean_data_client.delete(
        "/data/forgesteel-homebrew-settings/unknown", headers=user_headers
    )
    assert response.status_code == 404

    response = clean_data_client.put(
        "/data/forgesteel-homebrew-settings/123",
        json={"id": "123", "foo": "bar"},
        headers=user_headers,
    )
    assert response.status_code == 204

    ## FsHomebrews object exists, but no homebrew with given ID
    response = clean_data_client.delete(
        "/data/forgesteel-homebrew-settings/222", headers=user_headers
    )
    assert response.status_code == 404


def test_delete_homebrew_succeeds(clean_data_client, user_headers):
    homebrew_id = "123"
    endpoint = f"/data/forgesteel-homebrew-settings/{homebrew_id}"
    response = clean_data_client.put(
        endpoint,
        json={"id": homebrew_id, "foo": "bar"},
        headers=user_headers,
    )
    assert response.status_code == 204

    response = clean_data_client.delete(endpoint, headers=user_headers)
    assert response.status_code == 204

    response = clean_data_client.get(endpoint, headers=user_headers)
    assert response.status_code == 404
