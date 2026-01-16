---
name: git-setup
description: Initialize git repository if needed, configure SSH remote URL, add, commit, and push changes. Use this when the user wants to commit and push changes or set up git with SSH authentication.
allowed-tools: Bash(git:*), Bash(test:*)
---

# Git Setup and Commit Skill

This skill handles git initialization, remote configuration with SSH, committing, and pushing changes.

## Workflow

### 1. Check if Git is Initialized

First, check if git is already initialized in the current directory:

```bash
test -d .git && echo "Git is initialized" || echo "Git not initialized"
```

### 2. Initialize Git (if needed)

If git is not initialized, run:

```bash
git init
```

Then ask the user for their GitHub repository SSH URL (format: `git@github.com:username/repo.git`)

### 3. Configure Remote URL

Check existing remotes:

```bash
git remote -v
```

If no remote exists or initialization just happened, add the origin remote using the SSH URL provided:

```bash
git remote add origin git@github.com:username/repo.git
```

If the remote already exists and needs updating:

```bash
git remote set-url origin git@github.com:username/repo.git
```

### 4. Check Git Status

Before committing, always show the current status:

```bash
git status
```

### 5. Stage Changes

Add all changes to staging:

```bash
git add .
```

Show what was staged:

```bash
git status
```

### 6. Create Commit

Ask the user for a commit message, then create the commit with co-authorship:

```bash
git commit -m "$(cat <<'EOF'
<commit message>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

### 7. Verify Commit

Show the commit was created successfully:

```bash
git log -1 --oneline
git status
```

### 8. Push to Remote

Push the committed changes to the remote repository:

```bash
git push
```

If this is the first push or the branch has no upstream, use:

```bash
git push -u origin main
```

## Important Notes

- **SSH Authentication**: This skill is configured for SSH key authentication. Make sure the user has SSH keys set up with GitHub.
- **First Push**: For new repositories or branches without upstream, use `git push -u origin main` (or `master` depending on default branch)
- **Commit Messages**: Always ask the user for a meaningful commit message that describes the changes
- **Review Changes**: Show the user what files will be committed before creating the commit

## Error Handling

- If git is already initialized, skip the init step
- If remote already exists, ask before overwriting
- If there are no changes to commit, inform the user
- If SSH keys are not configured, guide the user to set them up
