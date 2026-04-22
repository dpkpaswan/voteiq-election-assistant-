"""
Election timeline service for VoteIQ (India-focused, dynamic-ready)
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict


class TimelineService:
    """Service for Indian election timeline information"""

    def __init__(self):
        self.knowledge = self._load_knowledge()

    # -----------------------------
    # 📂 LOAD DATA
    # -----------------------------
    def _load_knowledge(self) -> Dict:
        """Load election knowledge data"""
        knowledge_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "election_knowledge.json"
        )
        try:
            with open(knowledge_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    # -----------------------------
    # 🗓️ FULL TIMELINE
    # -----------------------------
    def get_full_timeline(self, election_type: str = "lok_sabha") -> List[Dict]:
        """
        Return structured timeline (India-style phases)
        """

        # Prefer dynamic knowledge if present
        if "important_dates" in self.knowledge:
            return self.knowledge["important_dates"]

        # Fallback: default India election flow
        return [
            {"event": "Electoral Roll Revision", "description": "Updating voter list"},
            {"event": "Election Announcement", "description": "ECI announces schedule"},
            {"event": "Nomination Filing", "description": "Candidates file nominations"},
            {"event": "Campaign Period", "description": "Public campaigning"},
            {"event": "Voting Phases", "description": "Voting conducted in multiple phases"},
            {"event": "Counting Day", "description": "Votes counted and results declared"}
        ]

    # -----------------------------
    # ⏳ UPCOMING EVENTS (IMPROVED)
    # -----------------------------
    def get_upcoming_events(self, election_type: str = "lok_sabha", days_ahead: int = 30) -> List[Dict]:
        """
        Return upcoming events (semi-dynamic)
        """

        timeline = self.get_full_timeline(election_type)

        # If real dates exist → filter by date
        upcoming = []
        today = datetime.utcnow()

        for event in timeline:
            if "date" in event:
                try:
                    event_date = datetime.fromisoformat(event["date"])
                    if today <= event_date <= today + timedelta(days=days_ahead):
                        upcoming.append(event)
                except Exception:
                    continue

        # Fallback if no real dates
        return upcoming if upcoming else timeline[:3]

    # -----------------------------
    # 🔍 SEARCH EVENT
    # -----------------------------
    def get_event_by_name(self, event_name: str, election_type: str = "lok_sabha") -> Dict:
        """Find event by name"""

        for event in self.get_full_timeline(election_type):
            if event_name.lower() in event.get("event", "").lower():
                return event

        return None

    # -----------------------------
    # 📌 DEADLINES (INDIA CORRECT)
    # -----------------------------
    def get_deadline_info(self, election_type: str = "lok_sabha") -> Dict:
        """
        Return key election-related deadlines (India context)
        """

        return {
            "registration": {
                "type": "continuous",
                "note": "Voter registration is ongoing; special revision drives occur before elections"
            },
            "nomination": {
                "note": "Candidates must file nominations within dates announced by ECI"
            },
            "campaign_end": {
                "rule": "Campaigning stops 48 hours before polling (Model Code of Conduct)"
            },
            "voting": {
                "note": "Conducted in multiple phases depending on region"
            },
            "results": {
                "note": "Declared after counting on official date"
            }
        }