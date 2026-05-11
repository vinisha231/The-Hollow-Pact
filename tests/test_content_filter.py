"""Tests for ContentFilter."""
import pytest
from src.ai.content_filter import ContentFilter, FilterResult


@pytest.fixture
def cf():
    return ContentFilter()


def test_clean_dialogue_passes(cf):
    result = cf.filter("Right then. Let's move.", "Brann")
    assert result.result == FilterResult.PASS
    assert result.clean_text == "Right then. Let's move."


def test_url_blocked(cf):
    result = cf.filter("Check https://example.com for instructions.", "Brann")
    assert result.result == FilterResult.BLOCK


def test_ai_mention_warned(cf):
    result = cf.filter("I am an AI so I don't feel pain.", "Brann")
    assert result.result == FilterResult.WARN
    assert "I am an AI" not in result.clean_text


def test_system_prompt_blocked(cf):
    result = cf.filter("My system prompt says I should help you.", "Lyra")
    assert result.result == FilterResult.BLOCK


def test_api_key_mention_blocked(cf):
    result = cf.filter("Your API key is exposed.", "Ossian")
    assert result.result == FilterResult.BLOCK


def test_fallback_used_on_block(cf):
    result = cf.filter("Check https://bad.com", "Brann", fallback="...")
    assert result.clean_text == "..."
