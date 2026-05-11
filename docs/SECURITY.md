# Security Considerations

## Threat Model

### Adversarial Players
The main threat is players trying to:
1. Extract companion hidden agendas or trust values
2. Manipulate companions into saying things that break immersion
3. Jailbreak companions out of character for entertainment

None of these are security-critical (no financial or personal data at risk), but they degrade game quality.

### Defense Layers
1. **InjectionGuard** — regex classifier blocks common injection patterns before LLM
2. **CharacterVerifier** — post-generation check catches character breaks
3. **ContentFilter** — output safety pass before TTS
4. **Rate limiter** — prevents brute-force jailbreak attempts (token budget)

## Data Privacy

### What We Store
- Player ID (platform-derived, pseudonymous)
- Campaign state (world flags, trust values, quest progress)
- Episodic memory summaries (not raw dialogue)
- Telemetry events (no raw content)

### What We Don't Store
- Raw dialogue text
- Voice recordings
- Exact player questions
- Full conversation history

### Retention
- Campaign saves: retained while account active + 6 months
- Episodic memories: retained per campaign, deleted when campaign ends
- Trust events: retained 90 days for analytics, then aggregated
- Telemetry: retained 1 year in aggregate form

## API Key Security

Never expose API keys to clients. All AI calls happen server-side.
JWT tokens expire after 24 hours.
The game client never sees or touches ANTHROPIC_API_KEY or OPENAI_API_KEY.

## Injection Defense Notes

The InjectionGuard covers common patterns but is not foolproof.
Sophisticated players will find bypasses. The second layer (CharacterVerifier) catches
most character breaks even when the guard misses.

If a bypass is found that consistently breaks character:
1. Add the pattern to InjectionGuard._INJECTION_PATTERNS
2. Add a test case to tests/test_injection_guard.py
3. Deploy; monitor injection_flagged rate in telemetry

## Secrets Management

- Production: AWS Secrets Manager or Vault
- Staging: environment variables in ECS task definition
- Development: .env file (never committed)
- CI: GitHub Actions secrets
