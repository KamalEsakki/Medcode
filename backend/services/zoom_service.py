import re
import urllib.parse
from typing import Optional, Dict, Any, List, Tuple
from backend.config import settings

ZOOM_URL_PATTERN = re.compile(
    r"^https?://(?:[a-zA-Z0-9_\-]+\.)*zoom\.us/(?:j|w|wc/join|my)/([a-zA-Z0-9]+)(?:\?.*)?$",
    re.IGNORECASE
)

DEMO_CONSULTATION_DIALOGUES: Dict[str, List[Dict[str, str]]] = {
    "Cardiology": [
        {"speaker": "Doctor", "text": "Hello, good afternoon Mr. Davis. I see you are joining for a cardiac follow-up. What symptoms have you been experiencing lately?", "delay_ms": 1200},
        {"speaker": "Patient", "text": "Good afternoon Doctor. I have been having substernal chest pain and shortness of breath whenever I climb stairs for the past 5 days.", "delay_ms": 1400},
        {"speaker": "Doctor", "text": "I see. Can you describe the chest pain? Does it radiate to your left arm, jaw, or shoulder?", "delay_ms": 1300},
        {"speaker": "Patient", "text": "Yes, it radiates to my left shoulder and jaw. It feels like a heavy squeezing pressure lasting about 15 minutes.", "delay_ms": 1500},
        {"speaker": "Doctor", "text": "Have you experienced any palpitations, lightheadedness, or swelling in your ankles?", "delay_ms": 1200},
        {"speaker": "Patient", "text": "A bit of ankle swelling in the evenings, yes.", "delay_ms": 1100},
        {"speaker": "Doctor", "text": "What medications are you currently taking, and have you taken anything for this episode?", "delay_ms": 1200},
        {"speaker": "Patient", "text": "I take Lisinopril 20mg daily for hypertension and Atorvastatin 40mg for high cholesterol. I took sublingual Nitroglycerin twice and it provided mild relief.", "delay_ms": 1600},
        {"speaker": "Doctor", "text": "Your resting blood pressure reading today is 148/92 mmHg with a heart rate of 84 bpm. Given the exertional substernal pressure radiating to the left shoulder and relief with nitroglycerin, this is consistent with unstable angina pectoris superimposed on chronic essential hypertension.", "delay_ms": 1800},
        {"speaker": "Doctor", "text": "We will order a 12-lead Electrocardiogram (ECG), serum Troponin labs, and schedule an urgent outpatient Transthoracic Echocardiogram. I am also adjusting your Lisinopril to 40mg and adding Metoprolol Succinate 25mg daily.", "delay_ms": 1800},
        {"speaker": "Patient", "text": "Thank you Doctor, I will get the ECG and blood work done immediately.", "delay_ms": 1200}
    ],
    "Pulmonology": [
        {"speaker": "Doctor", "text": "Hello Mrs. Taylor, thank you for joining the teleconsultation today. What primary symptoms bring you in?", "delay_ms": 1200},
        {"speaker": "Patient", "text": "Hello Doctor. I've been having high fever and a persistent wet cough producing yellowish-green sputum for three days, accompanied by right-sided chest discomfort when breathing deeply.", "delay_ms": 1500},
        {"speaker": "Doctor", "text": "Have you had any chills, night sweats, or difficulty catching your breath at rest?", "delay_ms": 1200},
        {"speaker": "Patient", "text": "Yes, shivering chills at night and moderate shortness of breath when walking across the room.", "delay_ms": 1300},
        {"speaker": "Doctor", "text": "Have you taken any medication for the fever or cough?", "delay_ms": 1100},
        {"speaker": "Patient", "text": "I took Paracetamol 650mg every 6 hours and OTC guaifenesin cough syrup with minimal improvement.", "delay_ms": 1400},
        {"speaker": "Doctor", "text": "Your home pulse oximeter shows SpO2 at 94% on room air, temperature 101.4°F, and respiratory rate 22 breaths/min. Based on acute fever, productive cough, pleuritic chest pain, and localized crackles, the clinical assessment indicates community-acquired bacterial pneumonia.", "delay_ms": 1800},
        {"speaker": "Doctor", "text": "We will prescribe oral Amoxicillin-Clavulanate 870/125mg twice daily for 7 days, Azithromycin 500mg daily, continue Paracetamol for fever, and order a two-view chest X-ray.", "delay_ms": 1700},
        {"speaker": "Patient", "text": "Understood Doctor, I will start the antibiotics today and get the X-ray.", "delay_ms": 1200}
    ],
    "General Practice": [
        {"speaker": "Doctor", "text": "Good morning. What symptoms have you been experiencing recently?", "delay_ms": 1200},
        {"speaker": "Patient", "text": "I have had fever, sore throat, and body aches for three days.", "delay_ms": 1300},
        {"speaker": "Doctor", "text": "Have you taken any medications or treatments so far?", "delay_ms": 1100},
        {"speaker": "Patient", "text": "I took Paracetamol and throat lozenges yesterday.", "delay_ms": 1200},
        {"speaker": "Doctor", "text": "Any nausea, vomiting, or breathing trouble?", "delay_ms": 1100},
        {"speaker": "Patient", "text": "No breathing trouble, just fatigue and mild nasal congestion.", "delay_ms": 1300},
        {"speaker": "Doctor", "text": "Examination shows erythematous pharynx without exudate. Assessment is acute viral upper respiratory infection. Continue hydration, Paracetamol for pain/fever, and rest.", "delay_ms": 1600},
        {"speaker": "Patient", "text": "Thank you Doctor.", "delay_ms": 1000}
    ]
}

class ZoomService:
    @staticmethod
    def validate_zoom_url(url: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str], str]:
        """
        Validates Zoom meeting link format and extracts meeting ID & passcode.
        Supports https://zoom.us/j/{id}, https://us04web.zoom.us/j/{id}, https://zoom.us/my/{vanity}, etc.
        """
        if not url or not isinstance(url, str):
            return False, None, None, None, "Meeting URL cannot be empty."

        clean_url = url.strip()
        
        # Check basic regex structure
        match = ZOOM_URL_PATTERN.match(clean_url)
        if not match:
            return False, None, None, None, (
                "Invalid Zoom URL. Format must be https://zoom.us/j/123456789 or https://*.zoom.us/j/123456789"
            )

        meeting_id = match.group(1)
        
        # Extract query parameters (e.g. ?pwd=xxx)
        parsed = urllib.parse.urlparse(clean_url)
        query_params = urllib.parse.parse_qs(parsed.query)
        passcode = query_params.get("pwd", [None])[0] or query_params.get("passcode", [None])[0]

        normalized_url = f"https://zoom.us/j/{meeting_id}"
        if passcode:
            normalized_url += f"?pwd={passcode}"

        return True, meeting_id, passcode, normalized_url, "Valid Zoom consultation meeting link."

    @staticmethod
    def is_real_zoom_configured() -> bool:
        """
        Checks if real Zoom Server-to-Server OAuth credentials are configured in settings.
        """
        return bool(
            settings.ZOOM_ACCOUNT_ID and 
            settings.ZOOM_CLIENT_ID and 
            settings.ZOOM_CLIENT_SECRET
        )

    @staticmethod
    def get_provenance_banner() -> Tuple[bool, str]:
        """
        Returns (is_demo_mode, status_label)
        """
        if ZoomService.is_real_zoom_configured() and settings.AI_MODE != "demo":
            return False, "AUTHENTICATED: Connected to Zoom Server-to-Server OAuth stream."
        return True, "DEMO MODE: Zoom connection simulated. Demo transcript — not received from a live Zoom meeting."

    @staticmethod
    def get_dialogue_for_consultation(specialty: Optional[str] = "Cardiology", consultation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generates structured dialogue utterances with timestamps and speaker tags.
        """
        template = DEMO_CONSULTATION_DIALOGUES.get(specialty or "General Practice", DEMO_CONSULTATION_DIALOGUES["Cardiology"])
        result = []
        elapsed = 0
        
        for item in template:
            elapsed += int(item.get("delay_ms", 1200) / 100)
            minutes = elapsed // 60
            seconds = elapsed % 60
            ts = f"{minutes:02d}:{seconds:02d}"
            
            result.append({
                "speaker": item["speaker"],
                "text": item["text"],
                "timestamp": ts,
                "consultationId": consultation_id,
            })
            
        return result

zoom_service = ZoomService()
