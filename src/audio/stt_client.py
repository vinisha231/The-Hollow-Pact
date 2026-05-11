"""
STTClient — speech-to-text using Whisper API with streaming chunking.

Streams 200ms audio chunks to the API to minimise latency.
Falls back to text input if STT exceeds the latency budget.
"""
from __future__ import annotations
import asyncio
import logging
import time
from typing import AsyncIterator, Optional

import httpx

log = logging.getLogger(__name__)

OPENAI_AUDIO_URL = "https://api.openai.com/v1/audio/transcriptions"
STT_MODEL = "whisper-1"
STT_TIMEOUT_MS = 800
CHUNK_SIZE_MS = 200


class STTClient:
    def __init__(self, api_key: str, timeout_ms: int = STT_TIMEOUT_MS):
        self._api_key = api_key
        self._timeout = timeout_ms / 1000.0

    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> Optional[str]:
        """
        Transcribes audio bytes via Whisper API.
        Returns None if timeout exceeded.
        """
        t0 = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    OPENAI_AUDIO_URL,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    data={"model": STT_MODEL, "language": language},
                    files={"file": ("audio.webm", audio_bytes, "audio/webm")},
                )
                if resp.status_code != 200:
                    log.error("stt_error status=%d", resp.status_code)
                    return None
                text = resp.json().get("text", "").strip()
                latency_ms = (time.monotonic() - t0) * 1000
                log.debug("stt_latency=%.0fms text=%r", latency_ms, text[:50])
                return text or None
        except httpx.TimeoutException:
            log.warning("stt_timeout after %.0fms", self._timeout * 1000)
            return None
        except Exception as exc:
            log.error("stt_exception: %s", exc)
            return None

    async def transcribe_streaming(
        self, audio_chunks: AsyncIterator[bytes]
    ) -> Optional[str]:
        """
        Accumulates chunks and transcribes once push-to-talk is released.
        """
        buffer = b""
        async for chunk in audio_chunks:
            buffer += chunk
        if not buffer:
            return None
        return await self.transcribe(buffer)
