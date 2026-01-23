---
name: close-project
description: End-of-session workflow that updates CLAUDE.md with recent changes and commits/pushes to the front-end branch. Use this when finishing work on the project.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git:*), Bash(find:*), Bash(ls:*)
---

# Close Project Skill

This skill performs end-of-session cleanup by updating documentation and committing changes to the front-end branch.

## Workflow

### 1. Analyze Recent Changes

First, check what has changed in the codebase since last commit:

```bash
git status
git diff --stat
```

Review the changes to understand what needs to be documented:
- New files or scripts added
- Modified configurations
- New features or components
- Changed workflows or commands

### 2. Read Current CLAUDE.md

Read the existing CLAUDE.md to understand what's already documented:

```
Read CLAUDE.md
```

### 3. Update CLAUDE.md

Edit CLAUDE.md to reflect recent changes. Focus on:

- New or changed development commands
- New scripts or tools added
- Architectural changes
- Updated directory structure (if files were added)
- New workflows or procedures

**Guidelines:**
- Keep the existing structure and formatting
- Only add/update sections relevant to the changes
- Don't remove existing documentation unless it's outdated
- Be concise - document the "what" and "how", not every detail

### 4. Stage All Changes

Add all changes including the updated CLAUDE.md:

```bash
git add .
```

Review what will be committed:

```bash
git status
git diff --staged --stat
```

### 5. Commit Changes

Create a descriptive commit message summarizing the session's work:

```bash
git commit -m "$(cat <<'EOF'
<Summary of changes made this session>

- <Change 1>
- <Change 2>
- <Change 3>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

### 6. Push to front-end Branch

Ensure we're on the front-end branch and push:

```bash
git branch --show-current
git push origin front-end
```

If not on front-end branch:

```bash
git checkout front-end
git push origin front-end
```

### 7. Confirm Completion

Show the final status and the pushed commit:

```bash
git log -1 --oneline
git status
```

Report to the user:
- Summary of CLAUDE.md updates
- Commit hash and message
- Confirmation of push to front-end branch

## What to Update in CLAUDE.md

- **Directory Structure**: New files or folders
- **Commands**: New scripts, startup procedures, or CLI options
- **Dependencies**: New packages or tools required
- **Configuration**: Changed settings or environment variables
- **Architecture**: New components or patterns introduced

## What NOT to Update

- Minor code changes that don't affect usage
- Internal implementation details
- Temporary or debug changes
- Information already covered elsewhere

## Error Handling

- If no changes exist, inform the user and skip the commit
- If CLAUDE.md doesn't need updates, proceed with commit only
- If push fails, check branch status and remote configuration
- If on wrong branch, checkout front-end before pushing
