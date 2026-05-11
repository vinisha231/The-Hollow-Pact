# Architecture Overview

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT (Unity)                        │
│                                                             │
│  ┌──────────┐   ┌──────────────┐   ┌────────────────────┐  │
│  │  Input   │   │   Game UI    │   │  Audio Manager     │  │
│  │ (voice/  │   │  (HUD, map,  │   │  (TTS playback,    │  │
│  │  text)   │   │   dialogue)  │   │   voice lines)     │  │
│  └────┬─────┘   └──────────────┘   └────────────────────┘  │
│       │                                                     │
│  ┌────▼─────────────────────────────────────────────────┐  │
│  │              Companion Controller                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │  │
│  │  │ Behavior Tree│  │ Dialogue FSM │  │Trust Probe│  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └───────────┘  │  │
│  └─────────┼────────────────┼──────────────────────────┘  │
└────────────┼────────────────┼───────────────────────────────┘
             │  Mirror/NetCode│
┌────────────▼────────────────▼───────────────────────────────┐
│                    DEDICATED GAME SERVER                     │
│                                                             │
│  ┌───────────────────────┐   ┌───────────────────────────┐  │
│  │   World State Manager │   │  Event Bus (Redis Pub/Sub)│  │
│  │   (authoritative)     │   │                           │  │
│  └──────────┬────────────┘   └───────────────────────────┘  │
│             │                                               │
│  ┌──────────▼────────────────────────────────────────────┐  │
│  │              AI Orchestration Service                  │  │
│  │                                                       │  │
│  │  STT → Guard → Memory Retrieval → LLM → Intent Router│  │
│  └──────────┬────────────────────────────────────────────┘  │
└─────────────┼───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                    PLATFORM SERVICES                        │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ Postgres │ │ pgvector │ │   S3     │ │  ElevenLabs  │  │
│  │ (campaign│ │(episodic │ │(save     │ │  TTS API     │  │
│  │  state)  │ │ memory)  │ │ blobs)   │  └──────────────┘  │
│  └──────────┘ └──────────┘ └──────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

## Service Breakdown

### Client (Unity URP)
- Companion Controller manages behavior tree + dialogue state machine
- Mirror netcode handles movement prediction and world sync
- Audio Manager streams TTS audio with lipsync blendshapes

### Dedicated Game Server
- Authoritative for all combat-relevant state
- AI Orchestration Service runs on server to prevent client-side manipulation
- Redis Pub/Sub for cross-companion event notifications

### AI Orchestration Service
1. STT — Whisper API or on-device whisper.cpp
2. Guard — injection classifier, sanitizer
3. Memory Retrieval — pgvector semantic search
4. LLM — Claude Sonnet / GPT-4o / Llama 3 70B
5. Intent Router — dialogue to TTS, actions to behavior tree

### Platform Services
- **Postgres** — structured campaign state, character data, trust values
- **pgvector** — episodic memory embeddings
- **S3** — binary save blobs, voice pre-caches
- **ElevenLabs** — streaming TTS for companion voice
