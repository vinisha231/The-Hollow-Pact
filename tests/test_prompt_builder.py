"""Tests for PromptBuilder."""
import pytest
from src.ai.prompt_builder import PromptBuilder
from src.ai.trust_engine import TrustEngine, TrustState, TrustBand


def make_builder():
    return PromptBuilder(TrustEngine())


def test_build_includes_companion_name(brann_persona, trust_state):
    builder = make_builder()
    prompt = builder.build(brann_persona, trust_state, '{"zone":"hub"}', "recent: none")
    assert "Brann" in prompt


def test_build_includes_response_format(brann_persona, trust_state):
    builder = make_builder()
    prompt = builder.build(brann_persona, trust_state, '{"zone":"hub"}', "recent: none")
    assert '"intent"' in prompt
    assert '"dialogue"' in prompt


def test_build_includes_world_snapshot(brann_persona, trust_state):
    builder = make_builder()
    world = '{"zone": "saltmere", "act": 1}'
    prompt = builder.build(brann_persona, trust_state, world, "none")
    assert "saltmere" in prompt


def test_estimate_tokens_positive(brann_persona):
    builder = make_builder()
    estimate = builder.estimate_tokens(brann_persona, "some memory", '{"zone":"hub"}')
    assert estimate > 0


def test_audit_prompt_returns_dict(brann_persona):
    builder = make_builder()
    audit = builder.audit_prompt(brann_persona)
    assert "persona_estimated" in audit
    assert "backstory" in audit
    assert all(v >= 0 for v in audit.values())
