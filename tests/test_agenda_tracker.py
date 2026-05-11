"""Tests for AgendaTracker."""
import pytest
from src.ai.agenda_tracker import AgendaTracker
from src.ai.companion_persona import HiddenAgenda
from src.world.world_state import WorldState, CampaignFlags


def make_world(flags=None):
    world = WorldState("camp1", "hub", "day", 1, 1)
    if flags:
        for f in flags:
            world.flags.set(f)
    return world


def make_agenda(condition_key: str) -> HiddenAgenda:
    return HiddenAgenda(
        id="test_agenda",
        label="find_thing",
        description="Find the thing.",
        priority=1,
        reveal_condition=f"Check {condition_key}",
        completion_condition=f"When {condition_key}_complete is set",
    )


def make_persona(agenda):
    from src.ai.companion_persona import CompanionPersona, PersonalityVector, LoyaltyStance
    return CompanionPersona(
        companion_id="brann",
        name="Brann",
        archetype="knight",
        voice_id="v1",
        personality=PersonalityVector(35, 60, 75, 80, 30, 25),
        stance=LoyaltyStance.CONDITIONAL,
        agendas=[agenda],
        backstory="...",
        speech_patterns=[],
        taboos=[],
    )


def test_no_events_when_conditions_not_met():
    agenda = make_agenda("ironveil_deed")
    persona = make_persona(agenda)
    world = make_world()
    tracker = AgendaTracker()
    events = tracker.evaluate(persona, world, "player1")
    assert events == []


def test_reveal_event_when_flag_set():
    agenda = make_agenda("ironveil_deed")
    persona = make_persona(agenda)
    world = make_world(flags=["ironveil_deed"])
    tracker = AgendaTracker()
    events = tracker.evaluate(persona, world, "player1")
    assert any(e.event_type == "partial_reveal" for e in events)


def test_completion_event_when_complete_flag_set():
    agenda = make_agenda("ironveil_deed")
    persona = make_persona(agenda)
    world = make_world(flags=["ironveil_deed_complete"])
    tracker = AgendaTracker()
    events = tracker.evaluate(persona, world, "player1")
    assert any(e.event_type == "completed" for e in events)


def test_completed_agenda_skipped():
    from dataclasses import replace
    agenda = make_agenda("ironveil_deed")
    # Mark as completed
    completed = HiddenAgenda(
        id=agenda.id, label=agenda.label, description=agenda.description,
        priority=agenda.priority, reveal_condition=agenda.reveal_condition,
        completion_condition=agenda.completion_condition, completed=True,
    )
    persona = make_persona(completed)
    world = make_world(flags=["ironveil_deed_complete"])
    tracker = AgendaTracker()
    events = tracker.evaluate(persona, world, "player1")
    assert events == []
