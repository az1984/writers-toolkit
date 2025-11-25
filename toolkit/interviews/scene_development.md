# Scene Development Interview

## Initialization
1. Start with IMPORT? (yes/no)
   - Yes: Paste scene details
   - No: Begin fresh interview

## Special Commands
- `breakpoint`: Pauses interview to adjust approach
- `bundle`: Saves transcript to versioned file (auto-created before menu/reload)
- `reset`: Starts fresh with current responses
- `export`: Saves to intake file and provides copyable summary
- `menu`: Returns to question list (auto-bundles first)
- `reload`: Updates from source (auto-bundles first)

## Core Questions
1. **Scene Basics**:
   - POV character:
   - Location:
   - Timeline position:

2. **Content**:
   - Key actions:
   - Emotional beats:
   - Sensory details:

3. **Purpose**:
   - Plot advancement:
   - Character development:
   - Theme expression:

## Example Flow
```
User: IMPORT?
AI: Should I import existing scene details? (yes/no)
User: no
AI: Beginning new scene development...
User: Who is the POV character?
AI: Elena Vasquez
User: export
AI: Saving to Intake/scenes/elena_interrogation_20250830.md
AI: Copyable summary:
```
Scene: FBI Interrogation
POV: Elena Vasquez
Key Beat: Discovers supernatural evidence
Sensory: Coffee, flickering lights, tension
```

User: menu
AI: [Creating bundle: Versions/scene_v1.md]
AI: Select question category:
1. Scene Basics
2. Content
3. Purpose
```

## Output Options
1. Continuous save: `Intake/scenes/[timestamp].md`
2. Versioned bundle: `Versions/scene_v[#].md`
3. Tagged excerpts: `Intake/snippets/[tag].md`
