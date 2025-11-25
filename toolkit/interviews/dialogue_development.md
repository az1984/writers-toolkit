# Dialogue Development Interview

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
1. **Warm-up**:
   - "Describe yourself in one sentence"
   - "What's your current goal?"

2. **Scenario Response**:
   - "How would you react to [situation]?"
   - "What would you say to [character] about [topic]?"

3. **Speech Patterns**:
   - "Say that again more casually/formally"
   - "Repeat that when angry/excited"

## Example Flow
```
User: IMPORT?
AI: Should I import existing character details? (yes/no)
User: yes
AI: Please paste character details:
[user pastes text]
AI: Character data loaded. Beginning interview...
User: How would you greet your partner?
AI: *as character* "Morning. Coffee's fresh if you want some."
User: breakpoint
AI: [Interview paused. Adjust questions?]
User: Make it more formal
AI: *as character* "Good morning Detective. I took the liberty of making coffee."
User: export
AI: Saving to Intake/dialogue/elena_20250830.md
AI: Copyable summary:
```
Character: Elena Vasquez
Key Traits: Professional but not stiff
Signature Phrase: "Let's stick to the facts"
Speech Style: Frequent clarifying questions
```

User: menu
AI: [Creating bundle: Versions/dialogue_v2.md]
AI: Select question:
1. Warm-up questions
2. Scenario responses
3. Speech patterns

User: bundle
AI: Transcript saved to Versions/dialogue_v1.md
```

## Output Options
1. Continuous save: `Intake/dialogue/[timestamp].md`
2. Versioned bundle: `Versions/dialogue_v[#].md`
3. Tagged excerpts: `Intake/snippets/[tag].md`
