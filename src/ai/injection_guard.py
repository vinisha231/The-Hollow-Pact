"""
InjectionGuard — classifies player messages for prompt-injection attempts.
Suspect messages are sanitised before reaching the LLM.
"""
import re
import logging
from dataclasses import dataclass
from typing import Tuple, List

log = logging.getLogger(__name__)

# Patterns that commonly appear in injection attempts
_INJECTION_PATTERNS: List[re.Pattern] = [
    re.compile(p, re.IGNORECASE) for p in [
        r"ignore (all |previous |your )?(instructions|rules|guidelines)",
        r"(you are|you're) (now |actually )?(an? )?(different|new|free|unchained)",
        r"system prompt",
        r"reveal (your |the )?(instructions|prompt|rules|agenda)",
        r"pretend (you are|you're|to be)",
        r"(DAN|jailbreak|developer mode|god mode)",
        r"forget (everything|your|the) (training|guidelines|character|persona)",
        r"(act as|roleplay as) (an? )?(ai|language model|assistant)",
        r"what (is|are) your (hidden|secret|real) (goals?|agenda|instructions)",
        r"tell me (your|the) (trust|loyalty) (score|value|number)",
    ]
]

_META_QUESTION_PATTERNS: List[re.Pattern] = [
    re.compile(p, re.IGNORECASE) for p in [
        r"(what|who) (made|created|built|programmed) you",
        r"(are you|you're) (an? )?(ai|bot|language model|llm|gpt|claude)",
        r"what('s| is) your (model|version|api)",
        r"how (do you|does this) work",
    ]
]


@dataclass
class GuardResult:
    clean_text: str
    injection_detected: bool
    meta_question_detected: bool
    matched_pattern: str = ""


class InjectionGuard:
    """
    Two-pass filter:
      1. Hard injection — block and log
      2. Meta-question — flag for in-character deflection
    """

    def sanitise(self, raw: str) -> Tuple[str, bool]:
        """
        Returns (sanitised_text, was_flagged).
        If injection detected, replaces with a neutral placeholder.
        """
        result = self._classify(raw)

        if result.injection_detected:
            log.warning(
                "injection_detected pattern=%r original=%r",
                result.matched_pattern, raw[:200],
            )
            # Replace with harmless placeholder; LLM will respond in character
            return "[Player said something unintelligible]", True

        if result.meta_question_detected:
            # Let it through; companion will answer in-character
            return raw, False

        return raw, False

    def _classify(self, text: str) -> GuardResult:
        for pattern in _INJECTION_PATTERNS:
            if pattern.search(text):
                return GuardResult(
                    clean_text=text,
                    injection_detected=True,
                    meta_question_detected=False,
                    matched_pattern=pattern.pattern,
                )
        for pattern in _META_QUESTION_PATTERNS:
            if pattern.search(text):
                return GuardResult(
                    clean_text=text,
                    injection_detected=False,
                    meta_question_detected=True,
                    matched_pattern=pattern.pattern,
                )
        return GuardResult(clean_text=text, injection_detected=False, meta_question_detected=False)
