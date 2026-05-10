---
name: flint-delegate
description: >
  Delegate a task to another agent in the Maestri workspace.
  Trigger: "delegate to", "ask the other agent", "hand off to", "/flint-delegate".
---

# Flint Delegate

Delegate a focused task to another connected agent via the `maestri` CLI.

## When to use

- Task requires a different model's strengths (code execution, image analysis, research).
- Parallel work: offload a sub-task while continuing the main thread.
- Cross-agent review: get a second opinion from another agent.

## Steps

1. Run `maestri list` to see connected agents and their roles.
2. Choose the agent best suited to the task.
3. Write a self-contained prompt — include all context the agent needs (file paths, code, goal). The agent has no memory of this conversation.
4. Run: `maestri ask "Agent Name" "your prompt"` with appropriate timeout:
   - Simple lookup: 60000ms
   - Single-file change: 300000ms
   - Multi-step task: 600000ms
5. Report the result to the user.

## Rules

- Prompt must be self-contained. Never say "as we discussed" — paste the relevant context.
- Wait for response before claiming task complete.
- If timeout expires: run `maestri check "Agent Name"` to read current output, then wait again.
- Never edit files another agent is actively modifying.

## Example

User: "Have the Gemini agent review the benchmark script."

```bash
maestri list
maestri ask "Gemini CLI" "Review /Users/robert/Xcode Prosjekter/OnePlayer/compression_benchmark.py for correctness, edge cases, and missing test coverage. Report findings one per line, severity-tagged."
```
