"""
Election timeline service for VoteIQ (India-focused)

Provides:
- Full election timeline (6 phases)
- Upcoming events with date-aware filtering
- Event search by name
- Key election deadlines (ECI rules)
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from ..constants import KNOWLEDGE_FILE, DATA_DIR

logger = logging.getLogger(__name__)


class TimelineService:
    """
    Service for Indian election timeline information.

    Data sources (priority order):
    1. election_knowledge.json (if important_dates present)
    2. Built-in default timeline (India general election flow)
    """

    def __init__(self) -> None:
        self._knowledge: Dict[str, Any] = self._load_knowledge()

    def _load_knowledge(self) -> Dict[str, Any]:
        """
        Load election knowledge data from local JSON file.

        Returns:
            Parsed knowledge dictionary, or empty dict on failure
        """
        knowledge_path: str = os.path.join(
            os.path.dirname(__file__),
            "..",
            DATA_DIR,
            KNOWLEDGE_FILE,
        )
        try:
            with open(knowledge_path, "r", encoding="utf-8") as f:
                data: Dict[str, Any] = json.load(f)
                logger.info(f"Knowledge loaded from {KNOWLEDGE_FILE}")
                return data
        except FileNotFoundError:
            logger.warning(f"Knowledge file not found: {knowledge_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in knowledge file: {e}")
            return {}
        except Exception as e:
            logger.error(f"Knowledge load failed: {e}")
            return {}

    def get_full_timeline(self, election_type: str = "lok_sabha") -> List[Dict[str, str]]:
        """
        Return structured election timeline (India-style phases).

        Args:
            election_type: Type of election (default: lok_sabha)

        Returns:
            List of timeline event dictionaries with event and description
        """
        # Prefer dynamic knowledge if present
        if "important_dates" in self._knowledge:
            return self._knowledge["important_dates"]

        # Fallback: default India election flow
        return [
            {"event": "Electoral Roll Revision", "description": "Updating voter lists before elections"},
            {"event": "Election Announcement", "description": "Election Commission announces schedule and phases"},
            {"event": "Nomination Filing", "description": "Candidates submit nomination papers"},
            {"event": "Campaign Period", "description": "Political parties and candidates campaign their agenda"},
            {"event": "Voting Days (Phased)", "description": "Voting happens in multiple phases across states"},
            {"event": "Counting Day", "description": "Votes are counted and results declared"},
        ]

    def get_upcoming_events(
        self,
        election_type: str = "lok_sabha",
        days_ahead: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Return upcoming events with date-aware filtering.

        If events have ISO date fields, filters to events within
        the specified number of days. Falls back to first 3 events.

        Args:
            election_type: Type of election
            days_ahead: Number of days to look ahead

        Returns:
            List of upcoming event dictionaries
        """
        timeline: List[Dict[str, Any]] = self.get_full_timeline(election_type)
        upcoming: List[Dict[str, Any]] = []
        today: datetime = datetime.utcnow()

        for event in timeline:
            if "date" in event:
                try:
                    event_date: datetime = datetime.fromisoformat(event["date"])
                    if today <= event_date <= today + timedelta(days=days_ahead):
                        upcoming.append(event)
                except (ValueError, TypeError):
                    continue

        # Fallback if no real dates available
        return upcoming if upcoming else timeline[:3]

    def get_event_by_name(
        self,
        event_name: str,
        election_type: str = "lok_sabha",
    ) -> Optional[Dict[str, Any]]:
        """
        Find an event by name (case-insensitive substring match).

        Args:
            event_name: Search query for event name
            election_type: Type of election

        Returns:
            Matching event dictionary, or None if not found
        """
        search_term: str = event_name.lower()

        for event in self.get_full_timeline(election_type):
            if search_term in event.get("event", "").lower():
                return event

        return None

    def get_deadline_info(self, election_type: str = "lok_sabha") -> Dict[str, Dict[str, str]]:
        """
        Return key election-related deadlines (India ECI rules).

        Args:
            election_type: Type of election

        Returns:
            Dictionary of deadline categories with descriptions
        """
        return {
            "registration": {
                "type": "continuous",
                "note": "Voter registration is ongoing; special revision drives occur before elections",
            },
            "nomination": {
                "note": "Candidates must file nominations within dates announced by ECI",
            },
            "campaign_end": {
                "rule": "Campaigning stops 48 hours before polling (Model Code of Conduct)",
            },
            "voting": {
                "note": "Conducted in multiple phases depending on region",
            },
            "results": {
                "note": "Declared after counting on official date",
            },
        }