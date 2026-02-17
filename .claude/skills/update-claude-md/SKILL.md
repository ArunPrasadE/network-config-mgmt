---
name: update-claude-md
description: Update CLAUDE.md to reflect recent codebase changes. Use this after adding new features, changing architecture, or modifying build commands.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(find:*), Bash(ls:*)
---

# Update CLAUDE.md Skill

This skill updates the CLAUDE.md file to reflect recent changes in the codebase.

## Workflow

### 1. Read Current CLAUDE.md

First, read the existing CLAUDE.md to understand what's documented:

```
Read CLAUDE.md
```

### 2. Analyze Recent Changes

Check what has changed in the codebase:

- Review package.json for new scripts or dependencies
- Check for new directories or components
- Look for architectural changes in key files (App.jsx, context files, etc.)
- Check for new hooks, utilities, or configuration files

### 3. Identify Updates Needed

Compare the current CLAUDE.md content against the codebase to identify:

- New or changed development commands
- New architectural patterns or components
- Changed state management approach
- New styling conventions
- Removed or deprecated features

### 4. Update CLAUDE.md

Edit CLAUDE.md to reflect the changes while following these guidelines:

- Keep the header intact:
  ```
  # CLAUDE.md

  This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
  ```
- Focus on the "big picture" architecture
- Document commands needed for development
- Don't list every file or component
- Don't include generic development practices
- Don't repeat information that can be easily discovered

### 5. Summarize Changes

After updating, provide a summary of what was changed in CLAUDE.md.

## What to Include

- Build, test, and development commands
- High-level architecture and patterns
- State management approach
- Key abstractions and their purposes
- Non-obvious conventions specific to this codebase

## What NOT to Include

- Obvious instructions or generic best practices
- Complete file listings
- Information easily discoverable by reading code
- Documentation that duplicates README.md
