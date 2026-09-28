import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def test_zoom_flow():
    print("========================================")
    print("Testing MedCode AI Zoom Consultation API")
    print("========================================")

    # 1. Test Zoom Link Validation (Valid URL)
    valid_url = "https://zoom.us/j/9876543210?pwd=clinicalPasscode123"
    res = requests.post(f"{BASE_URL}/zoom/validate", json={"meeting_url": valid_url})
    assert res.status_code == 200, f"Validate failed: {res.text}"
    val_data = res.json()
    print("[OK] Valid Zoom URL recognized successfully:")
    print(f"  Meeting ID: {val_data.get('meeting_id')}")
    print(f"  Passcode: {val_data.get('passcode')}")
    print(f"  Normalized URL: {val_data.get('normalized_url')}")

    # 2. Test Invalid Zoom Link
    res_bad = requests.post(f"{BASE_URL}/zoom/validate", json={"meeting_url": "https://notzoom.com/invalid"})
    assert res_bad.status_code == 400, "Should reject non-Zoom URL"
    print("[OK] Invalid URL properly rejected with 400 Bad Request.")

    # 3. Test Join Zoom Consultation (Demo Mode)
    join_payload = {
        "meeting_url": valid_url,
        "patient_name": "Robert Davis (Cardiac Teleconsult)",
        "patient_age": 58,
        "patient_gender": "Male",
        "doctor_name": "Dr. Sarah Lin, MD",
        "specialty": "Cardiology",
        "session_type": "Zoom Telehealth Consultation"
    }
    res_join = requests.post(f"{BASE_URL}/zoom/join", json=join_payload)
    assert res_join.status_code == 200, f"Join failed: {res_join.text}"
    join_data = res_join.json()
    session_id = join_data["session_id"]
    print("\n[OK] Zoom Consultation joined successfully:")
    print(f"  Session ID: {session_id}")
    print(f"  Session Code: {join_data['session_code']}")
    print(f"  Connection Status: {join_data['connection_status']}")
    print(f"  Audio Status: {join_data['audio_status']}")
    print(f"  Transcript Status: {join_data['transcript_status']}")
    print(f"  Demo Mode: {join_data['is_demo_mode']}")
    print(f"  Provenance Banner: {join_data['provenance_label']}")

    # 4. Test Session Status Polling
    res_status = requests.get(f"{BASE_URL}/zoom/status/{session_id}")
    assert res_status.status_code == 200, f"Get status failed: {res_status.text}"
    print("[OK] Zoom session status polled successfully.")

    # 5. Verify Transcript was seeded for this session
    res_transcript = requests.get(f"{BASE_URL}/transcripts/{session_id}")
    assert res_transcript.status_code == 200, f"Get transcript failed: {res_transcript.text}"
    tr_data = res_transcript.json()
    print(f"[OK] Initial permitted dialogue attached: {len(tr_data['dialogue'])} utterances, {tr_data['word_count']} words.")

    # 6. Test downstream pipeline execution: Clinical Note extraction
    res_note = requests.post(f"{BASE_URL}/clinical-notes/analyze/{session_id}")
    assert res_note.status_code == 200, f"Clinical note analysis failed: {res_note.text}"
    note_data = res_note.json()
    print(f"[OK] AI Clinical Note extracted: Chief Complaint = '{note_data['chief_complaint']}'")

    # 7. Test AI Code Suggestion generation
    res_codes = requests.post(f"{BASE_URL}/coding/analyze/{session_id}")
    assert res_codes.status_code == 200, f"Code generation failed: {res_codes.text}"
    codes_data = res_codes.json()
    print(f"[OK] Medical Code candidates generated: {len(codes_data)} candidate codes.")
    for c in codes_data:
        print(f"  [{c['code_type']}] {c['suggested_code']} - {c['clinical_concept']} ({c['confidence']}%)")

    # 8. Test Rule-based Scrubbing execution
    res_scrub = requests.post(f"{BASE_URL}/scrubbing/run/{session_id}")
    assert res_scrub.status_code == 200, f"Scrubbing failed: {res_scrub.text}"
    scrub_data = res_scrub.json()
    print(f"[OK] Scrubbing Engine completed: Status = {scrub_data['status']}, Passed = {scrub_data['passed_count']}, Warnings = {scrub_data['warning_count']}, Errors = {scrub_data['error_count']}")

    print("\n========================================")
    print("All Zoom Consultation pipeline tests PASSED!")
    print("========================================")

if __name__ == "__main__":
    try:
        test_zoom_flow()
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)
