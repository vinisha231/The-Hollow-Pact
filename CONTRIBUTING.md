# Contributing to The Hollow Pact

## Getting Started

```bash
# Clone and set up
git clone https://github.com/vinisha231/The-Hollow-Pact.git
cd The-Hollow-Pact
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Fill in your API keys in .env

# Start infrastructure
docker-compose up -d postgres redis

# Run tests
pytest
```

## Project Structure

```
src/
  ai/           — LLM orchestration, memory, trust, injection defense
  companion/    — Companion archetypes and loader
  combat/       — Behavior tree, betrayal system, enemy definitions
  multiplayer/  — Sessions, matchmaking, spotlight
  world/        — World state, quests, zones, mimic system
  audio/        — TTS client, bark library
  backend/      — Auth, save, telemetry
server/
  orchestration/ — FastAPI AI service
  matchmaking/   — FastAPI matchmaking microservice
docs/           — Design docs
assets/         — Visual specs, world design
tests/          — All test files
config/         — Designer-tunable defaults
```

## Key Principles

1. **Companions are people, not tools.** If a new feature makes companions more servile, push back.
2. **Trust must be earned and can be lost.** Don't add mechanics that give players free trust.
3. **Betrayals must be telegraphed.** Every hard betrayal needs 3+ hints in the codebase.
4. **LLM is not in the hot path.** No LLM calls per-frame, per-attack, or per-heal.
5. **Privacy-first.** Player conversations are ephemeral. No logging of raw dialogue content.

## Running Tests

```bash
pytest                          # all tests
pytest tests/test_trust_engine.py   # specific file
pytest -k "betrayal"             # keyword filter
pytest --cov=src                 # with coverage
```

## Code Style

Ruff for linting: `ruff check src/ tests/`
No comments explaining what the code does — only why if non-obvious.
Type hints on all public functions.

## Adding a New Companion

1. Add a JSON entry to `src/companion/archetypes.json`
2. Create a visual spec in `assets/companions/`
3. Add bark lines to `src/audio/bark_library.json`
4. Verify the companion passes the 5-line voice test (see `docs/COMPANION_DESIGN.md`)
5. Add at least 2 unit tests for their agenda logic

## Pull Requests

- Branch from `main`
- All tests must pass
- Ruff must report no errors
- Include a brief note on how betrayal behaviour was tested (if relevant)
