"""Tests for SpotlightSystem."""
import time
import pytest
from src.multiplayer.spotlight_system import SpotlightSystem, SpotlightRequest


def test_first_request_granted():
    system = SpotlightSystem()
    system.register_companion("brann", "player1")
    req = SpotlightRequest("brann", "player1", "direct_address", urgency=1.0)
    assert system.request_spotlight(req) is True


def test_direct_address_always_wins():
    system = SpotlightSystem()
    system.register_companion("brann", "player1")
    system.register_companion("lyra", "player2")
    # Lyra speaks first
    system.request_spotlight(SpotlightRequest("lyra", "player2", "idle", urgency=0.5))
    # Brann gets direct addressed
    result = system.request_spotlight(SpotlightRequest("brann", "player1", "direct_address", urgency=1.0))
    assert result is True


def test_second_companion_blocked_during_window():
    system = SpotlightSystem()
    system.register_companion("brann", "player1")
    system.register_companion("lyra", "player2")
    system.request_spotlight(SpotlightRequest("brann", "player1", "direct_address", urgency=1.0))
    result = system.request_spotlight(SpotlightRequest("lyra", "player2", "idle", urgency=0.3))
    assert result is False


def test_unregistered_companion_blocked():
    system = SpotlightSystem()
    req = SpotlightRequest("unknown", "player1", "idle", urgency=1.0)
    assert system.request_spotlight(req) is False


def test_release_allows_new_speaker():
    system = SpotlightSystem()
    system.register_companion("brann", "player1")
    system.register_companion("lyra", "player2")
    system.request_spotlight(SpotlightRequest("brann", "player1", "direct_address", urgency=1.0))
    system.release_spotlight("brann")
    result = system.request_spotlight(SpotlightRequest("lyra", "player2", "direct_address", urgency=1.0))
    assert result is True
