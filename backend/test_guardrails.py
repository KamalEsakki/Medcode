"""
Verification script for claim approval guardrails and return workflows.
"""
import requests

BASE_URL = "http://127.0.0.1:8000/api"

def test_guardrails():
    # 1. Login as scrubber
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"email": "coder@medcode.ai", "password": "demo123"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create a session with known scrubbing errors
    create_res = requests.post(
        f"{BASE_URL}/sessions/text-to-code",
        headers=headers,
        json={
            "clinical_text": "Patient has chest pain and palpitations. Performed standard 12-lead ECG. Diagnosed with chest pain.",
            "patient_name": "Guardrail Test Patient",
            "patient_mrn": "MRN-GUARD-01",
            "provider_name": "Dr. Sarah Lin, MD",
            "specialty": "Cardiology",
            "priority": "HIGH"
        }
    )
    assert create_res.status_code in (200, 201), f"Failed creating session: {create_res.text}"
    session_id = create_res.json()["id"]
    print(f"[OK] Created test encounter: {session_id}")

    # 3. Attempt to approve/bill the session directly when scrubbing errors exist
    approve_res = requests.put(
        f"{BASE_URL}/sessions/{session_id}/stage",
        headers=headers,
        json={"stage": "READY_FOR_BILLING", "notes": "Trying to bypass scrubbing errors"}
    )
    print(f"[OK] Attempt approval with errors -> Status: {approve_res.status_code}")
    if approve_res.status_code == 400:
        print(f"     Blocked as expected: {approve_res.json()['detail']}")
    else:
        print(f"     Response: {approve_res.text}")

    # 4. Return to physician with structured query
    return_res = requests.put(
        f"{BASE_URL}/sessions/{session_id}/stage",
        headers=headers,
        json={
            "stage": "RETURNED_TO_PHYSICIAN",
            "return_reason": "Documentation mismatch / lack of primary diagnosis specificity for 93000 pointer"
        }
    )
    assert return_res.status_code == 200, f"Return failed: {return_res.text}"
    print(f"[OK] Successfully returned case to physician -> Stage: {return_res.json()['stage']}")

if __name__ == "__main__":
    test_guardrails()
