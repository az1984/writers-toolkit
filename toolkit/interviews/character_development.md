# Character Development Interview

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
1. **Basic Info**:
   - Character's full name:
   - Age:  
   - Gender:
   - Role in story:

2. **Physical Traits**:
   - Appearance:
   - Distinctive features:
   - Style of dress:

3. **Personality**:
   - Key traits (3-5):
   - Core motivation:  
   - Biggest fear:

4. **Story Role**:
   - Main plot function:
   - Key relationships:
   - Character arc:

## Example Flow
```
User: IMPORT?
AI: Should I import existing character details? (yes/no)
User: yes
AI: Please paste character details:
[user pastes text]
AI: Character data loaded. Beginning interview...
User: What's the character's full name?
AI: Elena Vasquez
User: export
AI: Saving to Intake/characters/elena_20250830.md
AI: Copyable summary:
```
Character: Elena Vasquez
Role: FBI agent protagonist
Key Traits: Intelligent, determined, skeptical
Core Motivation: Prove supernatural has logical explanations
```

User: menu
AI: [Creating bundle: Versions/character_v2.md]
AI: Select question category:
1. Basic Info
2. Physical Traits  
3. Personality
4. Story Role
```

## Output Options
1. Continuous save: `Intake/characters/[timestamp].md`
2. Versioned bundle: `Versions/character_v[#].md`
3. Tagged excerpts: `Intake/snippets/[tag].md`
