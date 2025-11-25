# Location Creation Interview

## Initialization
1. Start with IMPORT? (yes/no)
   - Yes: Paste location details
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
   - Location name:
   - Type (city/region/natural):
   - Geographic features:

2. **Cultural Aspects**:
   - Inhabitants:
   - Architecture/style:
   - Notable customs:

3. **Story Role**:
   - Key events here:
   - Character connections:
   - Symbolic significance:

## Example Flow
```
User: IMPORT?
AI: Should I import existing location details? (yes/no)
User: no
AI: Beginning new location creation...
User: What's the location name?
AI: The Glass Peaks
User: export
AI: Saving to Intake/locations/glass_peaks_20250830.md
AI: Copyable summary:
```
Location: The Glass Peaks
Type: Mountain range
Features: Shimmering crystalline formations
Significance: Dragon nesting grounds
```

User: menu
AI: [Creating bundle: Versions/location_v1.md]
AI: Select question category:
1. Basic Info
2. Cultural Aspects
3. Story Role
```

## Output Options
1. Continuous save: `Intake/locations/[timestamp].md`
2. Versioned bundle: `Versions/location_v[#].md`
3. Tagged excerpts: `Intake/snippets/[tag].md`
