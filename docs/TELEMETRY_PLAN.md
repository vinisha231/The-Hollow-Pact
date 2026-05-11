# Telemetry Plan

## Why Telemetry is Critical for This Game

The Hollow Pact is one of the first AI-character games. We don't have data on:
- How fast trust changes feel satisfying vs arbitrary
- Which betrayal beats feel earned vs cheap
- Whether players detect soft betrayals or miss them
- How long players maintain hostile-trust companions before quitting

Telemetry answers these questions so we can tune them.

## Events to Capture

### Trust Events
Every `trust_changed` event includes:
- companion_id, player_id, campaign_id
- event_type (the named trust event)
- delta, trust_after, trust_band
- session_id (so we can trace full sessions)

**Why:** Lets us see which events move trust most/least. If `helped_villager` (+2) fires 20 times before `kept_promise` (+8) fires once, we might need to rebalance.

### Betrayal Events
Every `betrayal_triggered` event includes:
- beat_id, betrayal_type
- trust_at_trigger
- how many soft betrayals preceded this hard one

**Why:** We want to know if players are surprised (means we telegraphed poorly) or if they saw it coming (means we telegraphed well).

### Dialogue Quality
Every `dialogue_turn` includes:
- latency_ms (STT, LLM, TTS separately)
- model_used, tokens_used, cost_estimate
- intent
- injection_flagged (did the player try to jailbreak?)
- trust_band at time of turn

**Why:** Latency monitoring, cost tracking, jailbreak attempt rate.

### Session-Level
Every `session_ended` includes:
- duration_minutes
- player_count
- final trust band per companion

**Why:** Retention analysis. Do longer sessions have higher final trust? Do 4-player sessions end with lower trust than solo?

## What We DON'T Log

- Raw dialogue content (privacy)
- Player voice audio (never)
- Player's actual words (only classification metadata — "was injection detected")

## Dashboards to Build

1. **Trust Flow Dashboard** — histogram of trust values at session end per companion. We want a distribution, not a spike at 50.

2. **Betrayal Rate Dashboard** — % of campaigns reaching each betrayal beat. Target: 30-40% reach a hard betrayal in Act 1.

3. **Latency Dashboard** — P50/P95/P99 per stage per region. Alert: P95 > 2s.

4. **Cost Dashboard** — cost per player per hour per session. Alert: > $0.80/hr.

5. **Injection Attempt Rate** — % of turns that hit the injection guard. We expect 1-5% in live ops.

## Tuning Loop

Weekly:
- Review trust event frequency distribution
- Check betrayal funnel (how many players reached each beat)
- Review latency P95 by region

Monthly:
- Companion trust sentiment analysis (are players generally gaining or losing trust?)
- Cost per hour trend
- Injection pattern analysis (new patterns to add to guard?)
