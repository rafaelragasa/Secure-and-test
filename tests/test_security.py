"""Security tests — the most valuable tests you'll write this week.

Each one locks in an OWASP rule from Weeks 13-14 so a future change can't quietly
reopen the hole. ONE example is done; replace each `assert False` TODO with a real test.

Seed data reminder:  note 1 belongs to ALICE, note 2 belongs to BOB.
Accounts:  admin/admin123 (admin) · alice/alicepass · bob/bobpass
"""
from tests.conftest import login, auth


# ----- EXAMPLE (already done) ---------------------------------------------
def test_protected_route_rejects_no_token(client):
    res = client.get("/notes")               # no Authorization header
    assert res.status_code == 401            # A07: auth is required


# ----- TODO 1 -------------------------------------------------------------
def test_protected_route_rejects_bad_token(client):
    # Call GET /notes with a junk token, e.g. auth("not.a.jwt").
    # Assert 401 — the app must fail closed on an invalid token.
    response = client.get("/notes", headers=auth("not.a.jwt"))
    assert response.status_code == 401


# ----- TODO 2  (A01 — the big one) ----------------------------------------
def test_user_cannot_read_another_users_note(client):
    # Log in as alice. Try GET /notes/2 (that note belongs to Bob).
    # Assert 403 — ownership must be enforced.
    token = login(client, "alice", "alicepass")
    response = client.get("/notes/2", headers=auth(token))
    assert response.status_code == 403


# ----- TODO 3 -------------------------------------------------------------
def test_user_can_read_own_note(client):
    # Log in as alice. GET /notes/1 (hers). Assert 200.
    token = login(client, "alice", "alicepass")
    response = client.get("/notes/1", headers=auth(token))
    assert response.status_code == 200


# ----- TODO 4  (A07 — no user enumeration) --------------------------------
def test_login_does_not_reveal_which_field_was_wrong(client):
    # POST /login once with a username that doesn't exist, once with a real
    # username but wrong password. Assert the two error bodies are IDENTICAL.
    unknown_user = client.post("/login", json={"username": "missing", "password": "wrong"})
    wrong_password = client.post("/login", json={"username": "alice", "password": "wrong"})
    assert unknown_user.status_code == wrong_password.status_code == 401
    assert unknown_user.json() == wrong_password.json()


# ----- TODO 5  (A01 — role) -----------------------------------------------
def test_non_admin_cannot_list_users(client):
    # Log in as alice (not an admin). GET /admin/users. Assert 403.
    token = login(client, "alice", "alicepass")
    response = client.get("/admin/users", headers=auth(token))
    assert response.status_code == 403


# ----- TODO 6  (A04 — no hash leak) ---------------------------------------
def test_admin_can_list_users_without_password_leak(client):
    # Log in as admin. GET /admin/users. Assert 200 AND no item in the
    # response contains a "password" field.
    token = login(client, "admin", "admin123")
    response = client.get("/admin/users", headers=auth(token))
    assert response.status_code == 200
    assert all("password" not in user for user in response.json())
