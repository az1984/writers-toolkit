# Character Voice Interview

## Initialization
1. Start with IMPORT? (yes/no)
   - Yes: Paste character details
   - No: Begin fresh interview

## Special Commands
- `breakpoint`: Pauses interview to adjust approach
- `bundle`: Saves transcript to versioned file (auto-created before menu/reload)
- `reset`: Starts fresh with current responses
- `export`: Saves to intake file and provides copyable summary
- `menu`: Returns to question list (auto-bundles first)
- `reload`: Updates from source (auto-bundles first)

## Core Questions
1. **Narrative Style**:
   - 1st person thought patterns:
   - 3rd person descriptive style:
   - Emotional tone in narration:

2. **Perspective**:
   - How they perceive environments:
   - How they describe others:
   - Self-description tendencies:

3. **Voice Consistency**:
   - Changes under stress:
   - Evolution through story:
   - Unique linguistic quirks:

## Example Flow
```
User: IMPORT?
AI: Should I import character details? (yes/no)
User: yes
AI: Please paste character details:
[user pastes text]
AI: Character loaded. How does Elena describe herself in 1st person?
User: "I scan the room, noting every inconsistency"
User: export
AI: Saving to Intake/voices/elena_20250830.md
AI: Copyable summary:
```
Character: Elena Vasquez
1st Person: Analytical, detail-oriented
3rd Person: Precise, professional
Voice Quirk: Forensic terminology
```

User: menu
AI: [Creating bundle: Versions/voice_v1.md]
AI: Select question category:
1. Narrative Style
2. Perspective
3. Voice Consistency
```

## Output Options
1. Continuous save: `Intake/voices/[timestamp].md`
2. Versioned bundle: `Versions/voice_v[#].md`
3. Tagged excerpts: `Intake/snippets/[tag].md`
