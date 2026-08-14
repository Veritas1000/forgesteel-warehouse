def test_get_heroes_succeeds(clean_data_client, user_headers):
    response = clean_data_client.get("/data/forgesteel-heroes", headers=user_headers)

    assert response.status_code == 200
    assert response.json is not None
    assert "data" in response.json


def test_get_heroes_can_filter_returned_fields(clean_data_client, user_headers):
    response1 = clean_data_client.put(
        "/data/forgesteel-heroes/123",
        json={"id": "123", "foo": "bar"},
        headers=user_headers,
    )
    assert response1.status_code == 204
    response1a = clean_data_client.put(
        "/data/forgesteel-heroes/234",
        json={"id": "234", "name": "Foo Bar"},
        headers=user_headers,
    )
    assert response1a.status_code == 204

    response2 = clean_data_client.get(
        "/data/forgesteel-heroes?fields=name", headers=user_headers
    )
    assert response2.status_code == 200
    assert response2.json["data"] == [
        {"id": "123"},
        {"id": "234", "name": "Foo Bar"},
    ]

    response3 = clean_data_client.get(
        "/data/forgesteel-heroes?fields=id,foo", headers=user_headers
    )
    assert response3.status_code == 200
    assert response3.json["data"] == [
        {"id": "123", "foo": "bar"},
        {"id": "234"},
    ]


def test_get_unknown_hero_404s(clean_data_client, user_headers):
    ## No heroes object
    response = clean_data_client.get(
        "/data/forgesteel-heroes/unknown", headers=user_headers
    )
    assert response.status_code == 404

    response = clean_data_client.put(
        "/data/forgesteel-heroes/123",
        json={"id": "123", "foo": "bar"},
        headers=user_headers,
    )
    assert response.status_code == 204


def test_put_hero_succeeds(clean_data_client, user_headers):
    response = clean_data_client.put(
        "/data/forgesteel-heroes/123",
        json={"id": "123", "foo": "bar"},
        headers=user_headers,
    )

    assert response.status_code == 204


def test_put_hero_no_id_fails(clean_data_client, user_headers):
    response = clean_data_client.put(
        "/data/forgesteel-heroes/666",
        json={"foo": "bar"},
        headers=user_headers,
    )
    assert response.status_code == 400


def test_put_hero_mismatch_id_fails(clean_data_client, user_headers):
    response = clean_data_client.put(
        "/data/forgesteel-heroes/666",
        json={"id": "123", "foo": "bar"},
        headers=user_headers,
    )

    assert response.status_code == 400


def test_get_hero_returns_same_as_put(clean_data_client, user_headers):
    hero_data = {"id": "234", "foo": "baz"}
    endpoint = "/data/forgesteel-heroes/234"
    response = clean_data_client.put(
        endpoint,
        json=hero_data,
        headers=user_headers,
    )

    assert response.status_code == 204

    response2 = clean_data_client.get(endpoint, headers=user_headers)

    assert response2.status_code == 200
    assert response2.json["data"] == hero_data


def test_put_hero_updates_existing(clean_data_client, user_headers):
    hero_id = "345"
    hero_data = {"id": hero_id, "foo": "baz"}
    endpoint = f"/data/forgesteel-heroes/{hero_id}"
    response1 = clean_data_client.put(
        endpoint,
        json=hero_data,
        headers=user_headers,
    )

    assert response1.status_code == 204

    response2 = clean_data_client.get(endpoint, headers=user_headers)

    assert response2.status_code == 200
    assert response2.json["data"] == hero_data

    hero_data2 = {"id": hero_id, "foo": "bam", "name": "FooBar"}
    response3 = clean_data_client.put(
        endpoint,
        json=hero_data2,
        headers=user_headers,
    )

    assert response3.status_code == 204

    response4 = clean_data_client.get(endpoint, headers=user_headers)
    assert response4.status_code == 200
    assert response4.json["data"] == hero_data2


def test_put_single_hero_returned_with_full_list(clean_data_client, user_headers):
    hero_id = "456"
    hero_data = {"id": hero_id, "foo": "baz"}
    endpoint = f"/data/forgesteel-heroes/{hero_id}"
    response1 = clean_data_client.put(
        endpoint,
        json=hero_data,
        headers=user_headers,
    )

    assert response1.status_code == 204

    response2 = clean_data_client.get("/data/forgesteel-heroes", headers=user_headers)
    assert response2.status_code == 200
    heroes_list = response2.json["data"]
    assert len(heroes_list) == 1
    assert heroes_list[0] == hero_data


def test_delete_hero_404s_on_nonexistent(clean_data_client, user_headers):
    ## no heroes object
    response = clean_data_client.delete(
        "/data/forgesteel-heroes/unknown", headers=user_headers
    )
    assert response.status_code == 404

    response = clean_data_client.put(
        "/data/forgesteel-heroes/123",
        json={"id": "123", "foo": "bar"},
        headers=user_headers,
    )
    assert response.status_code == 204

    ## FsHero object exists, but no hero with given ID
    response = clean_data_client.delete(
        "/data/forgesteel-heroes/222", headers=user_headers
    )
    assert response.status_code == 404


def test_delete_hero_succeeds(clean_data_client, user_headers):
    hero_id = "123"
    endpoint = f"/data/forgesteel-heroes/{hero_id}"
    response = clean_data_client.put(
        endpoint,
        json={"id": hero_id, "foo": "bar"},
        headers=user_headers,
    )
    assert response.status_code == 204

    response = clean_data_client.delete(endpoint, headers=user_headers)
    assert response.status_code == 204

    response = clean_data_client.get(endpoint, headers=user_headers)
    assert response.status_code == 404
