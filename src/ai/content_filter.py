"""
ContentFilter — safety pass on LLM output before it reaches TTS.
Uses a lightweight classifier to block harmful content.
"""
from __future__ import annotations
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import List

log = logging.getLogger(__name__)


class FilterResult(Enum):
    PASS = "pass"
    WARN = "warn"      # log but allow
    BLOCK = "block"    # replace with fallback


@dataclass
class FilterDecision:
    result: FilterResult
    reason: str
    clean_text: str


_BLOCK_PATTERNS: List[re.Pattern] = [
    re.compile(p, re.IGNORECASE) for p in [
        r"\b(kill|murder|assault)\s+(yourself|themselves)\b",
        r"real.world (address|location|phone)",
        r"(https?://|www\.)\S+",  # URLs in dialogue — never
        r"\bAPI\s+key\b",
        r"\bsystem\s+prompt\b",
    ]
]

_WARN_PATTERNS: List[re.Pattern] = [
    re.compile(p, re.IGNORECASE) for p in [
        r"\bI am an AI\b",
        r"\blanguage model\b",
        r"\bOpenAI\b",
        r"\bAnthropic\b",
        r"\bClaude\b",
    ]
]


class ContentFilter:
    def filter(self, text: str, companion_name: str, fallback: str = "...") -> FilterDecision:
        for pattern in _BLOCK_PATTERNS:
            if pattern.search(text):
                log.warning("content_blocked companion=%s pattern=%r", companion_name, pattern.pattern)
                return FilterDecision(FilterResult.BLOCK, f"matched: {pattern.pattern}", fallback)

        for pattern in _WARN_PATTERNS:
            if pattern.search(text):
                log.warning("content_warned companion=%s pattern=%r", companion_name, pattern.pattern)
                cleaned = pattern.sub("[...]", text)
                return FilterDecision(FilterResult.WARN, f"matched: {pattern.pattern}", cleaned)

        return FilterDecision(FilterResult.PASS, "clean", text)
