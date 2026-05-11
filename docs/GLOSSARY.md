# Glossary

**Trust Band** — The coarse emotional tier a companion is currently in: Devoted, Loyal, Neutral, Suspicious, Hostile. Determines dialogue tone and unlocks betrayal branches. Never shown to the player numerically.

**Trust Value** — The hidden integer (0-100) underlying the trust band. Starts at 50 (Neutral). Players infer it through companion behaviour, never read it directly.

**Hidden Agenda** — A secret goal the companion is pursuing throughout the campaign. Players discover it through observation, not notification. Each companion has 1-3 agendas of varying priority.

**Betrayal Beat** — A defined narrative moment (entering a boss room, reaching a treasure vault) where a low-trust companion may choose to act against the party. Betrayal beats are scripted, not random.

**Soft Betrayal** — A betrayal behaviour that doesn't end the companion relationship: sandbagging in combat, hoarding loot, selling intel. Reversible if trust recovers.

**Hard Betrayal** — A betrayal behaviour that permanently changes the companion's relationship to the party: desertion, stealing the macguffin, turning hostile. Irreversible. The companion becomes a recurring antagonist NPC.

**Telegraph** — A hint or clue that foreshadows a betrayal. Each hard betrayal beat requires at least 3 telegraphs in the companion's dialogue and behaviour before it fires.

**Spotlight System** — The mechanism that prevents multiple companions from speaking simultaneously in multiplayer. One companion holds the "spotlight" per 5-second window; direct address overrides the queue.

**Bark** — A short, pre-generated combat voice line. Barks are generated offline and cached; they're played by the behavior tree with no LLM involvement, achieving near-zero latency.

**Episodic Memory** — A summarised record of a gameplay episode stored in a vector database (pgvector). Retrieved by semantic similarity when building the companion's LLM prompt.

**Semantic Fact** — A structured world-fact stored in Postgres: e.g. "player_gave_locket = Ruby gave silver locket in Act 2". Edited explicitly by the orchestrator, not by the LLM.

**Injection Guard** — The classifier that runs on every player message before it reaches the LLM, blocking prompt injection attempts and meta-questions.

**Character Verifier** — The post-generation check that ensures LLM responses stay in character and don't leak system information. Runs after the LLM, before TTS.

**Personality Vector** — The six numeric sliders (warmth, ambition, honesty, courage, deception tolerance, loyalty threshold) that shape a companion's personality. Set at campaign start and never mutated.

**Hathora** — The on-demand game server hosting platform used for dedicated party server instances. Each party session spins up its own Hathora room.

**Orchestration Service** — The FastAPI Python service that handles the full AI pipeline: STT → guard → memory retrieval → LLM → intent routing.
