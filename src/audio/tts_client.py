"""
TTSClient — streaming text-to-speech via ElevenLabs.
Buffers audio chunks for Unity to stream via AudioSource.
"""
from __future__ import annotations
import asyncio
import logging
from typing import AsyncIterator, Optional
import httpx

log = logging.getLogger(__name__)

ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"
STREAM_CHUNK_SIZE = 4096
DEFAULT_MODEL = "eleven_turbo_v2_5"


class TTSClient:
    def __init__(self, api_key: str, latency_optimisation: int = 3):
        self._api_key = api_key
        self._latency = latency_optimisation  # 0-4; 3 = low latency mode

    async def stream_speech(
        self,
        voice_id: str,
        text: str,
        model_id: str = DEFAULT_MODEL,
        stability: float = 0.5,
        similarity_boost: float = 0.8,
    ) -> AsyncIterator[bytes]:
        """
        Yields raw MP3 audio chunks as they arrive from ElevenLabs.
        First chunk typically arrives within 200ms.
        """
        url = f"{ELEVENLABS_BASE}/text-to-speech/{voice_id}/stream"
        headers = {
            "xi-api-key": self._api_key,
            "Content-Type": "application/json",
        }
        body = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
            },
            "optimize_streaming_latency": self._latency,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            async with client.stream("POST", url, json=body, headers=headers) as resp:
                if resp.status_code != 200:
                    body_text = await resp.aread()
                    log.error("tts_error status=%d body=%r", resp.status_code, body_text[:200])
                    return

                async for chunk in resp.aiter_bytes(STREAM_CHUNK_SIZE):
                    if chunk:
                        yield chunk

    async def generate_bark_pack(
        self,
        voice_id: str,
        companion_id: str,
        barks: dict[str, list[str]],
    ) -> dict[str, list[bytes]]:
        """
        Pre-generates voice packs for combat barks.
        Returns {bark_type: [audio_bytes, ...]}
        """
        result: dict[str, list[bytes]] = {}
        for bark_type, lines in barks.items():
            result[bark_type] = []
            for line in lines:
                audio = b""
                async for chunk in self.stream_speech(voice_id, line):
                    audio += chunk
                result[bark_type].append(audio)
                log.info(
                    "bark_generated companion=%s type=%s len=%d",
                    companion_id, bark_type, len(audio),
                )
        return result
