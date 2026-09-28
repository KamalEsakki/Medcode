import re
import urllib.parse
from typing import Optional, Dict, Any, List, Tuple
from backend.config import settings
from backend.services.zoom_service import DEMO_CONSULTATION_DIALOGUES

TEAMS_URL_PATTERN = re.compile(
    r"^https?://(?:[a-zA-Z0-9_\-]+\.)*(?:teams\.microsoft\.com|teams\.live\.com)/(?:l/meetup-join|meet)/([^/?#]+)(?:\?.*)?$",
    re.IGNORECASE
)

class TeamsService:
    @staticmethod
    def validate_teams_url(url: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str], str]:
        """
        Validates Microsoft Teams meeting link format and extracts meeting ID & conference context.
        Supports https://teams.microsoft.com/l/meetup-join/{id} and https://teams.live.com/meet/{id}.
        """
        if not url or not isinstance(url, str):
            return False, None, None, None, "Meeting URL cannot be empty."

        clean_url = url.strip()
        
        # Check basic regex structure or general teams domain
        if "teams.microsoft.com" not in clean_url.lower() and "teams.live.com" not in clean_url.lower():
            return False, None, None, None, (
                "Invalid Microsoft Teams URL. Format must be https://teams.microsoft.com/l/meetup-join/... or https://teams.live.com/meet/..."
            )

        match = TEAMS_URL_PATTERN.match(clean_url)
        raw_meeting_id = match.group(1) if match else "teams-encounter-call"
        
        # Extract query parameters (e.g. context, tid)
        parsed = urllib.parse.urlparse(clean_url)
        query_params = urllib.parse.parse_qs(parsed.query)
        tid = query_params.get("tid", [None])[0] or query_params.get("tenantId", [None])[0]

        normalized_url = clean_url
        clean_id = raw_meeting_id[:16] if len(raw_meeting_id) > 16 else raw_meeting_id

        return True, clean_id, tid, normalized_url, "Valid Microsoft Teams telehealth consultation link."

    @staticmethod
    def get_provenance_banner() -> Tuple[bool, str]:
        """
        Returns (is_demo_mode, status_label)
        """
        return True, "DEMO MODE: Microsoft Teams connection simulated. Demo transcript — not received from a live Teams meeting."

    @staticmethod
    def get_dialogue_for_consultation(specialty: Optional[str] = "Cardiology", consultation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generates structured dialogue utterances with timestamps and speaker tags for Teams.
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

teams_service = TeamsService()
