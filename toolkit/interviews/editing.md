# Editing Interview

## Initialization
1. Select chapter to review:
   - From existing chapters list
   - Or paste chapter text

## Special Commands
- `help`: Lists all available commands
- `breakpoint`/"pause"/"adjust": Pauses review to adjust focus
- `todo`/"task"/"fix": Creates actionable improvement item  
- `bundle`/"save"/"copy": Saves transcript to versioned file
- `resolve`/"done"/"complete": Marks todo as completed
- `compare`/"diff": Shows before/after versions
- `alternatives`/"options"/"versions": Generates comparison table
  - Saves to `book-memory-bank/Chapter_Alternatives/[todo_id].md`

## Fuzzy Matching Examples
```
User: Let's save this for later  
AI: Would you like to use the `bundle` command?
User: This isn't working
AI: Would you like to `reset` or `breakpoint`?
```

## Workflow
1. **Review**:
   - AI analyzes chapter elements:
     - Pacing
     - Characterization
     - Consistency
   - User asks specific questions

2. **Improvement**:
   - Create todos for changes
   - Discuss alternative approaches
   - Track decisions

3. **Tracking**:
   - Todos saved to `book-memory-bank/Chapter_Todos/[chapter].md`
   - Changes logged in `book-memory-bank/Core/progress.md`
   - Sidecar file links to chapter outline

## Example Flow
```
User: Review Chapter 3
AI: Chapter 3 Analysis:
- Pacing slows during middle
- Elena's motivation unclear
User: alternatives for Elena's dialogue
AI: | Version A | Version B |
   |-----------|-----------|
   | "I can't ignore the evidence" | "The facts don't lie" |
Saved to book-memory-bank/Chapter_Alternatives/3A.md
User: todo: Implement Version B with more intensity
AI: Added todo:
- [ ] Chapter 3: Use "facts don't lie" with stronger delivery
Linked to alternative 3A
```

## Output Options
1. Todo list: `book-memory-bank/Chapter_Todos/[chapter].md`
2. Progress tracking: Updated in `Core/progress.md`
3. Sidecar linkage: Connected to chapter outline
4. Revised chapter: `Chapters/[chapter]_revised.md`
