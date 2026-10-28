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


def test_closing_soon_filter_skips_deadlines_that_already_passed(client):
    from datetime import UTC, datetime, timedelta

    from app.demo_store import DEMO_STORE

    expired = DEMO_STORE.opportunities[0]
    expired.deadline_at = datetime.now(UTC) - timedelta(days=1)
    items = client.get("/api/v1/opportunities", params={"deadline_days": 7, "limit": 100}).json()["items"]
    slugs = {item["slug"] for item in items}
    assert expired.slug not in slugs
    assert slugs, "opportunities closing within the week should still be listed"


def test_profile_update_rejects_values_the_database_cannot_store(client, auth):
    for bad in ({"full_name": None}, {"full_name": ""}, {"degree": "x" * 101},
                {"graduation_year": 3000}, {"skills": ["x" * 101]}, {"skills": ["a"] * 51}):
        assert client.patch("/api/v1/me", json=bad, headers=auth).status_code == 422, bad


def test_null_lists_in_profile_update_become_empty_lists():
    from app.schemas import UpdateProfileRequest

    update = UpdateProfileRequest.model_validate({"skills": None, "preferred_domains": None})
    assert update.model_dump(exclude_unset=True) == {"skills": [], "preferred_domains": []}
    assert UpdateProfileRequest.model_validate({"full_name": "  Asha  "}).full_name == "Asha"


def test_public_listings_keep_their_cache_policy_and_private_data_is_not_cached(client, auth):
    assert client.get("/api/v1/opportunities").headers["cache-control"] == "public, max-age=60"
    assert "no-store" in client.get("/api/v1/me", headers=auth).headers["cache-control"]


def test_application_status_cannot_be_cleared(client, auth):
    app_id = client.get("/api/v1/applications", headers=auth).json()["items"][0]["id"]
    assert client.patch(f"/api/v1/applications/{app_id}", json={"status": None}, headers=auth).status_code == 422
    assert client.patch(f"/api/v1/applications/{app_id}", json={"note": "Follow up Friday"}, headers=auth).status_code == 200


def test_saved_search_rejects_values_the_columns_cannot_hold(client, auth):
    base = {"label": "Remote AI"}
    for bad in ({"mode": "x" * 31}, {"deadline_days": -3}, {"min_stipend": -1}, {"search": "q" * 256}):
        assert client.post("/api/v1/saved-searches", json={**base, **bad}, headers=auth).status_code == 422, bad
    assert client.post("/api/v1/saved-searches", json={**base, "mode": "remote", "deadline_days": 7},
                       headers=auth).status_code == 201


def test_recommendations_skip_closed_listings_and_ignore_case(client, auth):
    from datetime import UTC, datetime, timedelta

    from app.demo_store import DEMO_STORE

    closed = DEMO_STORE.opportunities[0]
    closed.deadline_at = datetime.now(UTC) - timedelta(days=2)
    DEMO_STORE.user.skills = [s.upper() for s in DEMO_STORE.opportunities[1].required_skills]
    DEMO_STORE.user.preferred_domains = [DEMO_STORE.opportunities[1].domain.upper()]

    slugs = [item["slug"] for item in client.get("/api/v1/opportunities/recommended", headers=auth).json()["items"]]
    assert closed.slug not in slugs
    assert slugs[0] == DEMO_STORE.opportunities[1].slug, "upper-case profile entries must still match"


def test_search_pattern_escapes_like_wildcards():
    from app.services import contains_pattern

    assert contains_pattern(" 100% ") == r"%100\%%"
    assert contains_pattern("c_plus") == r"%c\_plus%"
    assert contains_pattern(r"a\b") == r"%a\\b%"


def test_auth_log_masks_contact_details(caplog):
    import logging

    from app.audit_log import log_auth_event

    with caplog.at_level(logging.INFO, logger="auth"):
        log_auth_event("OTP_REQUEST", email="asha.verma@college.edu", phone="+919876543210")
    text = caplog.text
    assert "asha.verma@college.edu" not in text and "+919876543210" not in text
    assert "email=as********@college.edu" in text and "phone=***********10" in text


def test_rate_limiter_forgets_identifiers_after_a_day():
    from datetime import UTC, datetime, timedelta

    from app import rate_limiter

    now = datetime.now(UTC)
    rate_limiter.rate_limit_store["otp_request:old@example.com"] = [now - timedelta(days=2)]
    rate_limiter.rate_limit_store["otp_request:new@example.com"] = [now - timedelta(minutes=1)]
    rate_limiter._last_sweep = now - timedelta(hours=1)
    rate_limiter.sweep_stale_keys(now)
    assert "otp_request:old@example.com" not in rate_limiter.rate_limit_store
    assert "otp_request:new@example.com" in rate_limiter.rate_limit_store


def test_otp_requests_trigger_the_sweep():
    from datetime import UTC, datetime, timedelta

    from app import rate_limiter

    now = datetime.now(UTC)
    rate_limiter.rate_limit_store["otp_request:gone@example.com"] = [now - timedelta(days=3)]
    rate_limiter._last_sweep = now - timedelta(hours=1)
    rate_limiter.check_rate_limit("someone@example.com", limit=5, window_minutes=15)
    assert "otp_request:gone@example.com" not in rate_limiter.rate_limit_store
