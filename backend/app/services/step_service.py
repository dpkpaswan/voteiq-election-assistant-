"""
Step-by-step election guidance service for VoteIQ (India-focused)
"""

from typing import List
from ..models import ElectionStep


class StepService:
    """Service for providing step-by-step election guidance (India)"""

    # -----------------------------
    # 🗳️ REGISTRATION (Electoral Roll)
    # -----------------------------
    def get_registration_steps(self) -> ElectionStep:
        return ElectionStep(
            step_id="register",
            title="How to Register to Vote in India",
            description="Follow these steps to get your name added to the Electoral Roll.",
            actions=[
                "Check eligibility (Indian citizen, 18+ years, resident of constituency)",
                "Visit NVSP website or use Voter Helpline App",
                "Fill Form 6 (new voter registration)",
                "Upload required documents (age & address proof)",
                "Submit application online or via Booth Level Officer (BLO)",
                "Track application status online",
                "Receive your Voter ID (EPIC) after approval"
            ],
            estimated_time="10–20 minutes (online application)",
            resources=[
                "NVSP Portal (nvsp.in)",
                "Voter Helpline App",
                "Booth Level Officer (BLO)"
            ]
        )

    # -----------------------------
    # 🗳️ VOTING (EVM PROCESS)
    # -----------------------------
    def get_voting_steps(self) -> ElectionStep:
        return ElectionStep(
            step_id="voting",
            title="How to Vote in India (EVM Process)",
            description="Steps to cast your vote using Electronic Voting Machines (EVM).",
            actions=[
                "Check your name in the Electoral Roll",
                "Find your polling booth location",
                "Visit polling booth during voting hours (usually 7 AM – 6 PM)",
                "Carry Voter ID (EPIC) or valid alternative ID",
                "Get verified by polling officials",
                "Receive voter slip and proceed to voting compartment",
                "Press button on EVM for your chosen candidate",
                "Verify your vote via VVPAT slip display",
                "Exit polling booth after voting"
            ],
            estimated_time="10–15 minutes",
            resources=[
                "NVSP website for voter search",
                "Voter Slip information",
                "Election Commission guidelines"
            ]
        )

    # -----------------------------
    # 🪪 DOCUMENTS REQUIRED
    # -----------------------------
    def get_document_steps(self) -> ElectionStep:
        return ElectionStep(
            step_id="documents",
            title="Documents Required for Voting",
            description="Valid ID proofs accepted at polling booths.",
            actions=[
                "Carry your Voter ID (EPIC) if available",
                "If not, carry an alternative government ID",
                "Accepted IDs include Aadhaar, Passport, Driving License, PAN Card",
                "Ensure your name matches Electoral Roll",
                "Check voter slip for details before visiting"
            ],
            estimated_time="5 minutes preparation",
            resources=[
                "List of approved IDs by ECI",
                "Voter Helpline App"
            ]
        )

    # -----------------------------
    # 🏫 POLLING BOOTH PROCESS
    # -----------------------------
    def get_polling_steps(self) -> ElectionStep:
        return ElectionStep(
            step_id="polling",
            title="Polling Booth Process",
            description="What happens when you arrive at the polling station.",
            actions=[
                "Locate your assigned polling booth",
                "Stand in queue and wait for your turn",
                "Show ID proof to polling officer",
                "Get finger marked with indelible ink",
                "Receive permission to vote",
                "Cast vote using EVM",
                "Exit after successful voting"
            ],
            estimated_time="10–30 minutes (depends on queue)",
            resources=[
                "Polling booth info via NVSP",
                "Election Commission instructions"
            ]
        )

    # -----------------------------
    # 📊 RESULTS & COUNTING
    # -----------------------------
    def get_results_steps(self) -> ElectionStep:
        return ElectionStep(
            step_id="results",
            title="How Election Results Are Declared",
            description="Understanding vote counting and result declaration.",
            actions=[
                "EVMs are sealed and transported to counting centers",
                "Counting begins on officially announced day",
                "Votes are tallied constituency-wise",
                "VVPAT slips may be verified randomly",
                "Results are compiled and verified",
                "Winners are officially declared"
            ],
            estimated_time="Several hours (counting day)",
            resources=[
                "Election Commission results portal",
                "Official news sources"
            ]
        )

    # -----------------------------
    # 📦 ALL STEPS
    # -----------------------------
    def get_all_steps(self) -> List[ElectionStep]:
        return [
            self.get_registration_steps(),
            self.get_voting_steps(),
            self.get_document_steps(),
            self.get_polling_steps(),
            self.get_results_steps()
        ]