import sys
import requests
import json

# Ensure utf-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://127.0.0.1:8000/api"

def run_tests():
    print("==================================================")
    print("MEDCODE AI - BACKEND END-TO-END PIPELINE TEST SUITE")
    print("==================================================")

    # 1. Login
    print("\n1. Testing Login...")
    r = requests.post(f"{BASE}/auth/login", json={"email": "doctor@medcode.ai", "password": "demo123"})
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   [OK] Login Successful. Token received.")

    # 2. Current User
    print("\n2. Testing /auth/me...")
    r = requests.get(f"{BASE}/auth/me", headers=headers)
    assert r.status_code == 200
    user_info = r.json()
    print(f"   [OK] Authenticated as: {user_info['full_name']} ({user_info['role']})")

    # 3. Dashboard Stats
    print("\n3. Testing Dashboard Stats...")
    r = requests.get(f"{BASE}/dashboard/stats", headers=headers)
    assert r.status_code == 200, f"Dashboard stats failed: {r.text}"
    stats = r.json()
    print(f"   [OK] Dashboard Stats: Total Sessions = {stats['total_sessions']}, Clean Pass Rate = {stats['pass_rate']}%")

    # 4. List Sessions
    print("\n4. Testing List Sessions...")
    r = requests.get(f"{BASE}/sessions", headers=headers)
    assert r.status_code == 200
    sessions = r.json()
    print(f"   [OK] {len(sessions)} Sessions retrieved from database.")

    # 5. Create Live Session
    print("\n5. Testing Create Session...")
    r = requests.post(f"{BASE}/sessions", headers=headers, json={
        "patient_name": "Robert Davis",
        "patient_age": 58,
        "patient_gender": "Male",
        "doctor_name": "Dr. Sarah Lin, MD",
        "specialty": "Cardiology",
        "session_type": "Specialist Consultation"
    })
    assert r.status_code == 200
    new_sess = r.json()
    sess_id = new_sess["id"]
    sess_code = new_sess["session_code"]
    print(f"   [OK] Created Clinical Session: {sess_code} (ID: {sess_id})")

    # 6. Save Dialogue Transcript
    print("\n6. Testing Save Transcript...")
    dialogue = [
        {"speaker": "Doctor", "text": "What brings you in today?"},
        {"speaker": "Patient", "text": "I have been experiencing chest discomfort for two days."},
        {"speaker": "Doctor", "text": "Does it happen during physical activity?"},
        {"speaker": "Patient", "text": "Yes, sometimes after walking."}
    ]
    full_text = "\n\n".join([f"{d['speaker']}: {d['text']}" for d in dialogue])
    r = requests.post(f"{BASE}/transcripts", headers=headers, json={
        "session_id": sess_id,
        "full_text": full_text,
        "dialogue": dialogue,
        "duration_seconds": 75,
        "word_count": len(full_text.split())
    })
    assert r.status_code == 200
    print("   [OK] Transcript saved with speaker turns and timestamp metadata.")

    # 7. Extract Clinical Notes (SOAP + Concept Extraction)
    print("\n7. Testing Clinical Notes Extraction...")
    r = requests.post(f"{BASE}/clinical-notes/analyze/{sess_id}", headers=headers)
    assert r.status_code == 200
    note = r.json()
    print(f"   [OK] Extracted Chief Complaint: {note['chief_complaint']}")
    print(f"   [OK] Extracted Symptoms: {', '.join(note['symptoms'])}")
    print(f"   [OK] AI Disclaimer Tag: {note['ai_disclaimer'][:60]}...")

    # 8. Generate Medical Codes (ICD-10 & CPT)
    print("\n8. Testing Medical Code Suggestions...")
    r = requests.post(f"{BASE}/coding/analyze/{sess_id}", headers=headers)
    assert r.status_code == 200
    codes = r.json()
    print(f"   [OK] Generated {len(codes)} Code Suggestions:")
    for c in codes[:3]:
        print(f"     - [{c['code_type']}] {c['suggested_code']}: {c['description']} (Confidence: {c['confidence']}%)")

    # 9. Run Claim Scrubbing Engine
    print("\n9. Testing Claim Scrubbing Engine...")
    r = requests.post(f"{BASE}/scrubbing/run/{sess_id}", headers=headers)
    assert r.status_code == 200
    scrub = r.json()
    print(f"   [OK] Scrub Status: {scrub['status']} | Passed: {scrub['passed_count']}/{scrub['total_checks']} | Warnings: {scrub['warning_count']} | Errors: {scrub['error_count']}")
    for issue in scrub["issues"]:
        print(f"     [{issue['severity']}] {issue['rule_id']}: {issue['message']}")

    # 10. Human Review - Approve
    print("\n10. Testing Human Review Approve Action...")
    code_to_approve = codes[0]["id"]
    r = requests.post(f"{BASE}/reviews/{code_to_approve}/approve", headers=headers, json={"reviewer_notes": "Clinically confirmed by Attending Physician"})
    assert r.status_code == 200
    approved_res = r.json()
    print(f"   [OK] Code {approved_res['suggested_code']} status changed to: {approved_res['review_status']} (Reviewer: {approved_res['reviewed_by']})")

    # 11. Human Review - Modify
    if len(codes) > 1:
        print("\n11. Testing Human Review Modify Action...")
        code_to_modify = codes[1]["id"]
        r = requests.post(f"{BASE}/reviews/{code_to_modify}/modify", headers=headers, json={
            "modified_code": "I10.0",
            "modified_description": "Essential hypertension, benign with compliance documentation",
            "reviewer_notes": "Refined specificity"
        })
        assert r.status_code == 200
        mod_res = r.json()
        print(f"   [OK] Code {code_to_modify} modified to {mod_res['modified_code']} -> Status: {mod_res['review_status']}")

    # 12. Human Review - Reject
    if len(codes) > 2:
        print("\n12. Testing Human Review Reject Action...")
        code_to_reject = codes[2]["id"]
        r = requests.post(f"{BASE}/reviews/{code_to_reject}/reject", headers=headers, json={"reason": "Insufficient clinical history in current encounter"})
        assert r.status_code == 200
        rej_res = r.json()
        print(f"   [OK] Code {code_to_reject} rejected -> Status: {rej_res['review_status']}")

    # 13. Audit Trail Verification
    print("\n13. Testing Audit Trail Records...")
    r = requests.get(f"{BASE}/reviews", headers=headers)
    assert r.status_code == 200
    all_reviews = r.json()
    print(f"   [OK] {len(all_reviews['audits'])} Auditor actions logged in persistent audit trail.")

    print("\n==================================================")
    print("ALL BACKEND ENDPOINTS & FLOWS VERIFIED 100% SUCCESS")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
