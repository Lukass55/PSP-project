def test_tenant_isolation(client):
    tenant1 = client.post(
        "/tenants",
        json={"name": "Tenant 1"}
    )

    tenant2 = client.post(
        "/tenants",
        json={"name": "Tenant 2"}
    )

    assert tenant1.status_code == 200
    assert tenant2.status_code == 200

    tenant1_id = tenant1.json()["id"]
    tenant2_id = tenant2.json()["id"]

    user_ids = []

    for name in ["Lukas", "Tomas"]:
        response = client.post(
            f"/tenants/{tenant1_id}/users",
            json={"name": name, "surname": "Test"}
        )
        assert response.status_code == 200
        user_ids.append(response.json()["id"])

    group = client.post(
        f"/tenants/{tenant1_id}/groups",
        json={
            "name": "Privati grupė",
            "member_ids": user_ids
        }
    )

    assert group.status_code == 200
    group_id = group.json()["id"]

    # Pirmasis tenantas gali pasiekti savo grupę
    correct_response = client.get(
        f"/tenants/{tenant1_id}/groups/{group_id}/balances"
    )

    assert correct_response.status_code == 200
    assert correct_response.json()["group_name"] == "Privati grupė"

    # Antrojo tenanto ID netinka pirmajam priklausančiai grupei
    wrong_response = client.get(
        f"/tenants/{tenant2_id}/groups/{group_id}/balances"
    )

    assert wrong_response.status_code == 404
    assert wrong_response.json()["detail"] == "Grupė nerasta"