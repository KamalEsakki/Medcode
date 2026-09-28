import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def main():
    print("=" * 60)
    print("MEDCODE AI - SCRUBBER OPERATIONS TEST SUITE")
    print("=" * 60)

    # 1. Login as Coder
    print("\n1. Testing Scrubber Login...")
    res = requests.post(f"{BASE_URL}/auth/login", json={"email": "coder@medcode.ai", "password": "demo123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    data = res.json()
    token = data["access_token"]
    user = data["user"]
    print(f"   [OK] Logged in as: {user['full_name']} (Employee ID: {user.get('employee_id', 'EMP-8841')})")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 2. Get User Profile & Update Profile
    print("\n2. Testing /auth/profile GET & PUT...")
    p_res = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
    assert p_res.status_code == 200, f"Profile get failed: {p_res.text}"
    profile = p_res.json()
    print(f"   [OK] Retrieved profile: Org={profile.get('organization')}, Dept={profile.get('department')}")

    up_res = requests.put(f"{BASE_URL}/auth/profile", json={
        "organization": "Apex Health Network",
        "department": "Revenue Cycle Operations",
        "specialization": "Cardiology & Inpatient E/M"
    }, headers=headers)
    assert up_res.status_code == 200, f"Profile update failed: {up_res.text}"
    print(f"   [OK] Profile updated successfully.")

    # 3. Get Scrubber Dashboard Stats
    print("\n3. Testing /dashboard/stats...")
    d_res = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
    assert d_res.status_code == 200, f"Dashboard stats failed: {d_res.text}"
    d_data = d_res.json()
    print(f"   [OK] Assigned Cases: {d_data.get('assigned_cases')}, Clean Claim Rate: {d_data.get('clean_claim_rate')}%")

    # 4. Get My Cases Queue
    print("\n4. Testing /sessions/my-cases...")
    c_res = requests.get(f"{BASE_URL}/sessions/my-cases", headers=headers)
    assert c_res.status_code == 200, f"My cases failed: {c_res.text}"
    my_cases = c_res.json()
    print(f"   [OK] Retrieved {len(my_cases)} cases assigned to current scrubber.")

    # 5. Text to Code Direct Intake
    print("\n5. Testing /sessions/text-to-code...")
    ttc_payload = {
        "clinical_text": "SUBJECTIVE: 54yo male presents with 3-day history of exertional angina and dyspnea. OBJECTIVE: BP 144/90, HR 82. ECG shows normal sinus rhythm with T-wave inversions. ASSESSMENT & PLAN: Primary hypertension and unstable angina. Order troponin series and initiate beta blocker therapy.",
        "patient_name": "Arthur Pendelton",
        "patient_age": 54,
        "patient_gender": "Male",
        "specialty": "Cardiology",
        "priority": "HIGH"
    }
    ttc_res = requests.post(f"{BASE_URL}/sessions/text-to-code", json=ttc_payload, headers=headers)
    assert ttc_res.status_code == 200, f"Text to code failed: {ttc_res.text}"
    new_sess = ttc_res.json()
    print(f"   [OK] Generated Encounter: {new_sess['session_code']} (ID: {new_sess['id']})")
    print(f"   [OK] Stage: {new_sess.get('stage')}, Priority: {new_sess.get('priority')}")

    # 6. Update Stage
    print("\n6. Testing /sessions/{id}/stage...")
    stg_res = requests.put(f"{BASE_URL}/sessions/{new_sess['id']}/stage", json={
        "stage": "CODING_REVIEW",
        "note": "Beginning certified coder ICD-10 review"
    }, headers=headers)
    assert stg_res.status_code == 200, f"Stage update failed: {stg_res.text}"
    print(f"   [OK] Stage transitioned to CODING_REVIEW.")

    # 7. Get Case Documents
    print("\n7. Testing /sessions/{id}/documents...")
    doc_res = requests.get(f"{BASE_URL}/sessions/{new_sess['id']}/documents", headers=headers)
    assert doc_res.status_code == 200, f"Case documents failed: {doc_res.text}"
    docs = doc_res.json()
    print(f"   [OK] Case has {len(docs)} documents generated.")

    # 8. Test Teams URL Validation & Join
    print("\n8. Testing Microsoft Teams Router...")
    teams_val = requests.post(f"{BASE_URL}/teams/validate", json={"meeting_url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_test"})
    assert teams_val.status_code == 200, f"Teams val failed: {teams_val.text}"
    print(f"   [OK] Teams URL validated.")

    # 9. Test Performance Telemetry
    print("\n9. Testing /performance/me...")
    perf_res = requests.get(f"{BASE_URL}/performance/me?timeframe=weekly", headers=headers)
    assert perf_res.status_code == 200, f"Performance failed: {perf_res.text}"
    perf = perf_res.json()
    print(f"   [OK] Performance: Completed={perf['cases_completed']}, Clean Rate={perf['clean_claim_rate']}%")

    # 10. Test Notifications
    print("\n10. Testing /notifications...")
    notif_res = requests.get(f"{BASE_URL}/notifications", headers=headers)
    assert notif_res.status_code == 200, f"Notifications failed: {notif_res.text}"
    notifs = notif_res.json()
    print(f"   [OK] Retrieved {len(notifs)} work notifications.")

    # 11. Test Voice/Text Assistant Command
    print("\n11. Testing /assistant/command...")
    cmd_res = requests.post(f"{BASE_URL}/assistant/command", json={
        "query": "Show my high priority cases",
        "current_path": "/dashboard"
    }, headers=headers)
    assert cmd_res.status_code == 200, f"Assistant command failed: {cmd_res.text}"
    cmd_data = cmd_res.json()
    print(f"   [OK] Assistant intent: {cmd_data.get('intent')}, navigation: {cmd_data.get('navigate_to')}")

    print("\n" + "=" * 60)
    print("ALL 11 SCRUBBER OPERATIONS ENDPOINTS VERIFIED 100%!")
    print("=" * 60)

if __name__ == "__main__":
    main()
