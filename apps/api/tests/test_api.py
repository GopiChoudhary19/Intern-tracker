from uuid import uuid4


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_security_headers_present(client):
    h = client.get("/health").headers
    assert h["X-Content-Type-Options"] == "nosniff"
    assert h["X-Frame-Options"] == "DENY"


def test_list_opportunities_paginates(client):
    first = client.get("/api/v1/opportunities", params={"limit": 2}).json()
    assert len(first["items"]) == 2
    assert first["metadata"]["page"] == 1
    total = first["metadata"]["total"]
    assert first["metadata"]["has_next_page"] == (total > 2)


def test_list_opportunities_rejects_bad_limit(client):
    assert client.get("/api/v1/opportunities", params={"limit": 0}).status_code == 422
    assert client.get("/api/v1/opportunities", params={"limit": 101}).status_code == 422


def test_filter_by_type(client):
    items = client.get("/api/v1/opportunities", params={"type": "hackathon", "limit": 100}).json()["items"]
    assert items and all(i["type"] == "hackathon" for i in items)


def test_search_matches_organization_name(client):
    # "Google" only appears in the organisation field of the Google internship
    items = client.get("/api/v1/opportunities", params={"search": "google", "limit": 100}).json()["items"]
    assert [i["slug"] for i in items] == ["google-swe-internship-program"]


def test_opportunity_detail_and_404(client):
    slug = client.get("/api/v1/opportunities").json()["items"][0]["slug"]
    assert client.get(f"/api/v1/opportunities/{slug}").json()["slug"] == slug
    assert client.get("/api/v1/opportunities/does-not-exist").status_code == 404


def test_protected_routes_need_token(client):
    assert client.get("/api/v1/applications").status_code == 401
    assert client.get("/api/v1/applications", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.get("/api/v1/opportunities/recommended").status_code == 401


def test_demo_otp_login(client):
    r = client.post("/api/v1/auth/request-otp", json={"email": "Student@Example.edu"})
    assert r.status_code == 200 and r.json()["development_code"] == "000000"


def test_application_lifecycle(client, auth):
    opp = client.get("/api/v1/opportunities", params={"limit": 100}).json()["items"][-1]
    before = len(client.get("/api/v1/applications", headers=auth).json()["items"])

    r = client.post("/api/v1/applications", headers=auth, json={"opportunity_id": opp["id"], "status": "saved"})
    assert r.status_code == 201
    app_id = r.json()["id"]
    assert r.json()["applied_at"] is None

    r = client.patch(f"/api/v1/applications/{app_id}", headers=auth, json={"status": "applied", "note": "sent"})
    assert r.status_code == 200
    assert r.json()["status"] == "applied" and r.json()["applied_at"] is not None

    assert len(client.get("/api/v1/applications", headers=auth).json()["items"]) == before + 1
    assert client.delete(f"/api/v1/applications/{app_id}", headers=auth).status_code == 200
    assert len(client.get("/api/v1/applications", headers=auth).json()["items"]) == before


def test_create_application_validates_status_and_opportunity(client, auth):
    opp_id = client.get("/api/v1/opportunities").json()["items"][0]["id"]
    bad = client.post("/api/v1/applications", headers=auth, json={"opportunity_id": opp_id, "status": "banana"})
    assert bad.status_code == 400
    missing = client.post("/api/v1/applications", headers=auth, json={"opportunity_id": str(uuid4())})
    assert missing.status_code == 404


def test_admin_requires_token(client, admin):
    assert client.get("/api/v1/admin/opportunities").status_code == 401
    assert client.get("/api/v1/admin/opportunities", headers=admin).status_code == 200


def test_update_application_rejects_unknown_status(client, auth):
    app_id = client.get("/api/v1/applications", headers=auth).json()["items"][0]["id"]
    r = client.patch(f"/api/v1/applications/{app_id}", headers=auth, json={"status": "banana"})
    assert r.status_code == 400
    assert client.get("/api/v1/applications", headers=auth).json()["items"][0]["status"] != "banana"


def test_deleting_missing_records_returns_404(client, auth, admin):
    missing = uuid4()
    assert client.delete(f"/api/v1/applications/{missing}", headers=auth).status_code == 404
    assert client.delete(f"/api/v1/saved-searches/{missing}", headers=auth).status_code == 404
    assert client.delete(f"/api/v1/admin/opportunities/{missing}", headers=admin).status_code == 404


def test_saved_search_create_and_delete(client, auth):
    r = client.post("/api/v1/saved-searches", headers=auth, json={"label": "Remote backend", "mode": "Remote"})
    assert r.status_code == 201
    sid = r.json()["id"]
    assert client.delete(f"/api/v1/saved-searches/{sid}", headers=auth).status_code == 200
    assert client.delete(f"/api/v1/saved-searches/{sid}", headers=auth).status_code == 404
