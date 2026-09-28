import sys
import requests
import json
import uuid

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://127.0.0.1:8000/api"

def test_auth_flows():
    print("==================================================")
    print("MEDCODE AI - AUTHENTICATION FLOW VERIFICATION TEST")
    print("==================================================")

    # ----------------------------------------------------
    # TEST 1: EXISTING USER - Correct Credentials
    # ----------------------------------------------------
    print("\n[TEST 1] EXISTING USER: Correct Email + Correct Password")
    r = requests.post(f"{BASE}/auth/login", json={
        "email": "doctor@medcode.ai",
        "password": "demo123"
    })
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    token = r.json()["access_token"]
    user = r.json()["user"]
    print(f"  [OK] Login Success! User: {user['full_name']} ({user['email']})")

    # Verify /auth/me with valid token
    r_me = requests.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r_me.status_code == 200
    print(f"  [OK] Protected route /auth/me accessible for authenticated user.")

    # ----------------------------------------------------
    # TEST 2: EXISTING USER - Wrong Password
    # ----------------------------------------------------
    print("\n[TEST 2] EXISTING USER: Correct Email + Wrong Password")
    r = requests.post(f"{BASE}/auth/login", json={
        "email": "doctor@medcode.ai",
        "password": "WrongPassword999!"
    })
    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"
    err_detail = r.json().get("detail", "")
    print(f"  [OK] Login Rejected as expected (Status 401). Error message: '{err_detail}'")

    # ----------------------------------------------------
    # TEST 3: NON-EXISTING USER - Unknown Email + Any Password
    # ----------------------------------------------------
    print("\n[TEST 3] NON-EXISTING USER: Unknown Email + Any Password")
    unknown_email = f"unknown_{uuid.uuid4().hex[:6]}@randomhospital.org"
    r = requests.post(f"{BASE}/auth/login", json={
        "email": unknown_email,
        "password": "AnyRandomPassword123"
    })
    assert r.status_code == 404, f"Expected 404, got {r.status_code}: {r.text}"
    err_detail = r.json().get("detail", "")
    print(f"  [OK] Login Rejected with 404. Error message: '{err_detail}'")
    assert "Account not found" in err_detail, f"Expected 'Account not found' in message, got '{err_detail}'"

    # ----------------------------------------------------
    # TEST 4: NEW USER - Sign Up -> Account Created -> Login -> Logout
    # ----------------------------------------------------
    print("\n[TEST 4] NEW USER: Sign Up -> Account Created -> Login")
    new_email = f"dr.newuser_{uuid.uuid4().hex[:6]}@medcode.ai"
    new_pass = "SecurePass2026!"
    new_name = "Dr. Evelyn Vance, MD"

    # 4a. Register
    r_reg = requests.post(f"{BASE}/auth/register", json={
        "full_name": new_name,
        "email": new_email,
        "password": new_pass,
        "role": "physician"
    })
    assert r_reg.status_code == 200, f"Registration failed: {r_reg.text}"
    reg_user = r_reg.json()["user"]
    print(f"  [OK] Account Created: {reg_user['full_name']} ({reg_user['email']})")

    # 4b. Login with new user credentials
    r_new_login = requests.post(f"{BASE}/auth/login", json={
        "email": new_email,
        "password": new_pass
    })
    assert r_new_login.status_code == 200
    new_token = r_new_login.json()["access_token"]
    print(f"  [OK] New user login successful. Token issued.")

    # 4c. Duplicate Sign Up Prevention
    r_dup = requests.post(f"{BASE}/auth/register", json={
        "full_name": new_name,
        "email": new_email,
        "password": new_pass,
        "role": "physician"
    })
    assert r_dup.status_code == 400, f"Expected 400 on duplicate registration, got {r_dup.status_code}: {r_dup.text}"
    dup_detail = r_dup.json().get("detail", "")
    print(f"  [OK] Duplicate registration rejected (Status 400). Message: '{dup_detail}'")

    # ----------------------------------------------------
    # TEST 5: GOOGLE USER - Sign In (New Account and Existing Account)
    # ----------------------------------------------------
    print("\n[TEST 5] GOOGLE USER: Google Sign-In (New Account & Existing Account)")
    google_email = f"google.doctor_{uuid.uuid4().hex[:6]}@gmail.com"
    google_name = "Dr. Google Authenticated Specialist"

    # 5a. First-time Google Sign-In (Creates account automatically)
    r_g1 = requests.post(f"{BASE}/auth/google", json={
        "email": google_email,
        "full_name": google_name,
        "role": "physician"
    })
    assert r_g1.status_code == 200, f"Google login failed: {r_g1.text}"
    g_user1 = r_g1.json()["user"]
    g_token1 = r_g1.json()["access_token"]
    print(f"  [OK] First-time Google user created & logged in: {g_user1['full_name']} ({g_user1['email']})")

    # 5b. Subsequent Google Sign-In with same account (Logs in without creating duplicate)
    r_g2 = requests.post(f"{BASE}/auth/google", json={
        "email": google_email,
        "full_name": google_name,
        "role": "physician"
    })
    assert r_g2.status_code == 200
    g_user2 = r_g2.json()["user"]
    assert g_user1["id"] == g_user2["id"], "User IDs should match for existing Google account"
    print(f"  [OK] Existing Google user authenticated successfully. User ID preserved ({g_user2['id']}).")

    # ----------------------------------------------------
    # TEST 6: LOGOUT & PROTECTED ROUTE ACCESS BLOCK
    # ----------------------------------------------------
    print("\n[TEST 6] LOGOUT & UNPROTECTED ACCESS ATTEMPTS")
    # Call logout endpoint
    r_logout = requests.post(f"{BASE}/auth/logout")
    assert r_logout.status_code == 200
    print("  [OK] Backend logout acknowledged.")

    # Try accessing protected route with no token (e.g. after logout)
    r_unauth = requests.get(f"{BASE}/auth/me")
    assert r_unauth.status_code == 401, f"Expected 401 without token, got {r_unauth.status_code}"
    print("  [OK] Protected route /auth/me strictly rejects unauthenticated request (Status 401).")

    # Try accessing with invalid token
    r_bad_token = requests.get(f"{BASE}/auth/me", headers={"Authorization": "Bearer invalid_fake_token_12345"})
    assert r_bad_token.status_code == 401
    print("  [OK] Protected route strictly rejects invalid token (Status 401).")

    print("\n==================================================")
    print("ALL 6 AUTHENTICATION FLOW TESTS PASSED 100%!")
    print("==================================================")

if __name__ == "__main__":
    test_auth_flows()
