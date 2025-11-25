# Research Interview

## Initialization
1. Start with RESEARCH TOPIC:
   - User provides subject to investigate
   - AI confirms scope

## Special Commands
- `breakpoint`: Pauses research to adjust approach
- `bundle`: Saves transcript to versioned file
- `newtopic`: Switches to different research subject
- `record`: Saves findings to appropriate note file
- `modify`: Edits findings before recording

## Workflow
1. **Question Phase**:
   - User asks research questions
   - AI provides summarized answers

2. **Creative Phase**:
   - User modifies/synthesizes information
   - AI helps adapt for fictional use

3. **Recording**:
   - Saved to relevant project file:
     - `Research/[topic]/[date].md`
     - Cross-referenced in `activeContext.md`

## Example Flow
```
User: RESEARCH TOPIC: Police interrogation techniques
AI: Researching modern interrogation methods...
AI: Found: Reid technique, PEACE model, cognitive interviewing
User: How would these adapt for supernatural cases?
AI: Modified techniques might include:
- Truth magic detection
- Paranormal evidence handling
User: record
AI: Saved to Research/interrogation/20250830.md
```

## Output Options
1. Raw research: `Research/[topic]/raw/[date].md`
2. Adapted findings: `Research/[topic]/adapted/[date].md`
3. Integrated notes: Linked to relevant worldbuilding/character files
