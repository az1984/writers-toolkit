# Worldbuilding Interview

## Initialization
1. Start with IMPORT? (yes/no)
   - Yes: Paste worldbuilding details
   - No: Begin fresh interview

## Special Commands
- `breakpoint`: Pauses interview to adjust approach
- `bundle`: Saves transcript to versioned file (auto-created before menu/reload)
- `reset`: Starts fresh with current responses
- `export`: Saves to intake file and provides copyable summary
- `menu`: Returns to question list (auto-bundles first)
- `reload`: Updates from source (auto-bundles first)

## Core Questions
1. **Foundations**:
   - Core premise:
   - Key differences from reality:
   - Physical laws/rules:

2. **Cultural Systems**:
   - Power structures:
   - Economic models:
   - Social hierarchies:

3. **Implementation**:
   - How shown in story:
   - Character perspectives:
   - Consistency checks:

## Example Flow
```
User: IMPORT?
AI: Should I import existing worldbuilding? (yes/no)
User: no
AI: Beginning new worldbuilding session...
User: What's the core premise?
AI: A world where dragons bond with humans through shared consciousness
User: export
AI: Saving to Intake/worldbuilding/dragon_bond_20250830.md
AI: Copyable summary:
```
Core Premise: Dragon-human consciousness bonds
Key Rule: Magic requires equilibrium
Culture: Dragonrider meritocracy
```

User: menu
AI: [Creating bundle: Versions/worldbuilding_v1.md]
AI: Select question category:
1. Foundations
2. Cultural Systems
3. Implementation
```

## Output Options
1. Continuous save: `Intake/worldbuilding/[timestamp].md`
2. Versioned bundle: `Versions/worldbuilding_v[#].md`
3. Tagged excerpts: `Intake/snippets/[tag].md`
