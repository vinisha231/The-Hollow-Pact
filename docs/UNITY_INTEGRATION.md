# Unity Integration Notes

## Companion Controller Architecture

The companion controller in Unity bridges the Python AI backend to the game scene.

```
CompanionController.cs
├── DialogueManager        → sends voice/text to orchestration API, receives audio
├── BehaviorTreeRunner     → ticks the combat BT at 10Hz
├── TrustEventEmitter      → fires trust events to backend on game events
├── AnimationController    → drives blend shapes based on trust band
└── AudioManager          → streams TTS audio, plays bark cache
```

## API Communication

The Unity client communicates with the FastAPI orchestration service via:
- REST (HTTP/2): dialogue turns, trust events, session lifecycle
- No WebSocket for now — stateless request/response is simpler and sufficient

### Dialogue flow
```csharp
// 1. Player pushes PTT, records audio
// 2. Audio sent to STT (either locally or via server)
// 3. Transcribed text sent to /dialogue endpoint
// 4. Response (dialogue + intent) received
// 5. Audio streamed from TTS
// 6. Intent dispatched to behavior tree / world system
```

### Example C# stub
```csharp
public async Task<DialogueResponse> SendDialogue(string text, WorldSnapshot world) {
    var request = new DialogueRequest {
        SessionId = SessionManager.CurrentSessionId,
        CompanionId = companion.companionId,
        PlayerId = PlayerManager.LocalPlayerId,
        RawText = text,
        WorldState = world,
        CombatActive = CombatManager.IsActive
    };
    var json = JsonUtility.ToJson(request);
    using var httpClient = new HttpClient();
    var response = await httpClient.PostAsync(
        $"{ApiBaseUrl}/dialogue",
        new StringContent(json, Encoding.UTF8, "application/json")
    );
    return JsonUtility.FromJson<DialogueResponse>(await response.Content.ReadAsStringAsync());
}
```

## Blend Shape Driven Trust States

Trust bands drive companion facial blend shapes:
- `devotion_smile`: 0 (hostile) → 0.8 (devoted)
- `suspicion_squint`: 0 (devoted) → 0.9 (hostile)
- `guard_crossed_arms`: 0 (devoted) → 1.0 (hostile)
- `eye_contact_weight`: 0.9 (devoted) → 0.1 (hostile)

Transitions are lerped over 2 seconds to avoid jarring snaps.

## Audio Streaming

1. TTS audio streams as MP3 chunks from ElevenLabs
2. Chunks are fed into Unity's AudioSource via a ring buffer
3. Lipsync uses Oculus LipSync or similar blend-shape driver
4. Audio spatialization: 3D, attached to companion transform

## Bark Cache

Pre-baked barks are loaded on companion spawn:
- Stored as AudioClip assets in Resources/Companions/{companion_id}/barks/
- BT action nodes call `AudioManager.PlayBark(type)` which picks randomly from the loaded set
- No network call; zero latency

## Trust Event Firing

Game events → TrustEventEmitter → POST /trust_event:

```csharp
public async void OnPlayerAction(string actionType) {
    await trustEventEmitter.Send(new TrustEventRequest {
        CompanionId = companion.companionId,
        PlayerId = PlayerManager.LocalPlayerId,
        EventType = actionType,
        SessionId = SessionManager.CurrentSessionId
    });
}
```

Trust events fire from:
- Quest objective completion
- Dialogue branches that contain trust-relevant choices
- World interaction events (NPC interactions, loot decisions, etc.)
- Death/near-death of companion or player
