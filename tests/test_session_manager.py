"""Tests for SessionManager."""
import pytest
from unittest.mock import AsyncMock, patch
from src.multiplayer.session_manager import SessionManager, SessionState


@pytest.fixture
def manager():
    return SessionManager("app_123", "token_abc")


@pytest.mark.asyncio
async def test_create_session_returns_session(manager):
    session = await manager.create_session("campaign_xyz")
    assert session.campaign_id == "campaign_xyz"
    assert session.state == SessionState.LOBBY
    assert session.hathora_room_id is not None


@pytest.mark.asyncio
async def test_get_existing_session(manager):
    session = await manager.create_session("campaign_abc")
    fetched = await manager.get_session(session.session_id)
    assert fetched is not None
    assert fetched.session_id == session.session_id


@pytest.mark.asyncio
async def test_get_nonexistent_session(manager):
    result = await manager.get_session("nonexistent_id")
    assert result is None


@pytest.mark.asyncio
async def test_add_player_fills_slot(manager):
    session = await manager.create_session("campaign_abc")
    slot = session.add_player("player1", "char1", "brann")
    assert slot.player_id == "player1"
    assert slot.is_host is True
    assert session.player_count == 1


@pytest.mark.asyncio
async def test_first_player_is_host(manager):
    session = await manager.create_session("campaign_abc")
    session.add_player("player1", "char1", "brann")
    session.add_player("player2", "char2", "lyra")
    hosts = [s for s in session.slots if s.is_host]
    assert len(hosts) == 1
    assert hosts[0].player_id == "player1"


@pytest.mark.asyncio
async def test_host_reassigned_on_leave(manager):
    session = await manager.create_session("campaign_abc")
    session.add_player("player1", "char1", "brann")
    session.add_player("player2", "char2", "lyra")
    session.remove_player("player1")
    hosts = [s for s in session.slots if s.is_host]
    assert len(hosts) == 1
    assert hosts[0].player_id == "player2"


@pytest.mark.asyncio
async def test_session_full_raises(manager):
    session = await manager.create_session("campaign_abc")
    for i in range(4):
        session.add_player(f"player{i}", f"char{i}", "brann")
    with pytest.raises(ValueError, match="full"):
        session.add_player("player5", "char5", "brann")
