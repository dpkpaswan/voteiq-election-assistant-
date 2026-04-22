"""
Step service tests for VoteIQ
Tests step-by-step election guidance data
"""

import pytest
from app.services.step_service import StepService
from app.models import ElectionStep


class TestStepService:

    @pytest.fixture
    def service(self):
        return StepService()

    # -----------------------------
    # 📦 ALL STEPS
    # -----------------------------
    def test_get_all_steps_returns_list(self, service):
        steps = service.get_all_steps()
        assert isinstance(steps, list)
        assert len(steps) == 5

    def test_all_steps_are_election_step_type(self, service):
        steps = service.get_all_steps()
        for step in steps:
            assert isinstance(step, ElectionStep)

    def test_all_steps_have_unique_ids(self, service):
        steps = service.get_all_steps()
        ids = [s.step_id for s in steps]
        assert len(ids) == len(set(ids))

    # -----------------------------
    # 🗳️ REGISTRATION
    # -----------------------------
    def test_registration_step(self, service):
        step = service.get_registration_steps()
        assert step.step_id == "register"
        assert "Register" in step.title or "register" in step.title.lower()
        assert len(step.actions) > 0
        assert len(step.resources) > 0

    # -----------------------------
    # 🗳️ VOTING
    # -----------------------------
    def test_voting_step(self, service):
        step = service.get_voting_steps()
        assert step.step_id == "voting"
        assert "EVM" in step.title or "Vote" in step.title
        assert len(step.actions) > 3

    # -----------------------------
    # 🪪 DOCUMENTS
    # -----------------------------
    def test_documents_step(self, service):
        step = service.get_document_steps()
        assert step.step_id == "documents"
        assert len(step.actions) > 0
        # Should mention accepted IDs
        combined = " ".join(step.actions).lower()
        assert any(kw in combined for kw in ["aadhaar", "voter id", "epic", "passport"])

    # -----------------------------
    # 🏫 POLLING
    # -----------------------------
    def test_polling_step(self, service):
        step = service.get_polling_steps()
        assert step.step_id == "polling"
        assert len(step.actions) > 3

    # -----------------------------
    # 📊 RESULTS
    # -----------------------------
    def test_results_step(self, service):
        step = service.get_results_steps()
        assert step.step_id == "results"
        assert len(step.actions) > 3

    # -----------------------------
    # 📝 DATA QUALITY
    # -----------------------------
    def test_all_steps_have_estimated_time(self, service):
        for step in service.get_all_steps():
            assert step.estimated_time
            assert len(step.estimated_time) > 0

    def test_all_steps_have_resources(self, service):
        for step in service.get_all_steps():
            assert isinstance(step.resources, list)
            assert len(step.resources) > 0

    def test_steps_serializable(self, service):
        """Ensure steps can be serialized to dict (for JSON responses)"""
        for step in service.get_all_steps():
            data = step.model_dump()
            assert isinstance(data, dict)
            assert "step_id" in data
            assert "actions" in data
