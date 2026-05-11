"""Tests for CompanionPersona and PersonalityVector."""
import pytest
from src.ai.companion_persona import (
    CompanionPersona, PersonalityVector, HiddenAgenda, LoyaltyStance
)


def make_persona(**kwargs) -> CompanionPersona:
    defaults = dict(
        companion_id="brann_test",
        name="Brann",
        archetype="disgraced_knight",
        voice_id="v1",
        personality=PersonalityVector(
            warmth=35, ambition=60, honesty=75, courage=80,
            deception_tolerance=30, loyalty_threshold=25,
        ),
        stance=LoyaltyStance.CONDITIONAL,
        agendas=[],
        backstory="A knight who lost everything.",
        speech_patterns=["Right then.", "I've seen worse."],
        taboos=["Lord Caldrath"],
    )
    defaults.update(kwargs)
    return CompanionPersona(**defaults)


def test_system_prompt_includes_name():
    persona = make_persona()
    prompt = persona.system_prompt_block
    assert "Brann" in prompt


def test_system_prompt_includes_personality():
    persona = make_persona()
    prompt = persona.system_prompt_block
    assert "35" in prompt  # warmth value


def test_system_prompt_includes_taboos():
    persona = make_persona()
    prompt = persona.system_prompt_block
    assert "Lord Caldrath" in prompt


def test_system_prompt_includes_backstory():
    persona = make_persona()
    prompt = persona.system_prompt_block
    assert "lost everything" in prompt


def test_personality_vector_validates_range():
    with pytest.raises(ValueError):
        PersonalityVector(
            warmth=150, ambition=60, honesty=75, courage=80,
            deception_tolerance=30, loyalty_threshold=25,
        )


def test_persona_with_agendas():
    agenda = HiddenAgenda(
        id="a1", label="find_sister",
        description="Find my missing sister Kara.",
        priority=1,
        reveal_condition="party finds note",
        completion_condition="sister found",
    )
    persona = make_persona(agendas=[agenda])
    prompt = persona.system_prompt_block
    assert "missing sister" in prompt


def test_to_dict_roundtrip():
    persona = make_persona()
    d = persona.to_dict()
    restored = CompanionPersona.from_dict(d)
    assert restored.name == persona.name
    assert restored.personality.warmth == persona.personality.warmth
    assert restored.stance == persona.stance
