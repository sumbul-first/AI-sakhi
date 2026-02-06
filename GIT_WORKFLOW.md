# Git Workflow Guide for AI Sakhi

This guide explains the Git workflow for the AI Sakhi project.

## Repository Setup

The repository has been initialized with:
- ✅ `.gitignore` - Excludes Python cache, virtual environments, AWS credentials, logs
- ✅ `README.md` - Project overview and setup instructions
- ✅ `CONTRIBUTING.md` - Contribution guidelines
- ✅ `CHANGELOG.md` - Version history and changes
- ✅ Initial commit with complete codebase

## Branch Strategy

### Main Branches

- **`master`** (or `main`) - Production-ready code
  - Always stable and deployable
  - Protected branch (requires PR for changes)
  - Tagged with version numbers

### Supporting Branches

- **`feature/*`** - New features
  - Branch from: `master`
  - Merge back to: `master`
  - Example: `feature/sms-notifications`

- **`fix/*`** - Bug fixes
  - Branch from: `master`
  - Merge back to: `master`
  - Example: `fix/session-timeout-bug`

- **`docs/*`** - Documentation updates
  - Branch from: `master`
  - Merge back to: `master`
  - Example: `docs/api-documentation`

- **`test/*`** - Test additions
  - Branch from: `master`
  - Merge back to: `master`
  - Example: `test/integration-tests`

- **`refactor/*`** - Code refactoring
  - Branch from: `master`
  - Merge back: `master`
  - Example: `refactor/content-manager`

## Daily Workflow

### 1. Start Working on a New Feature

```bash
# Update your local master branch
git checkout master
git pull origin master

# Create a new feature branch
git checkout -b feature/your-feature-name

# Or use the alias (if configured)
git cob feature/your-feature-name
```

### 2. Make Changes

```bash
# Check status frequently
git status
# Or use alias
git st

# View changes
git diff
# Or use alias
git df

# Stage changes
git add .
# Or stage specific files
git add core/new_file.py tests/test_new_file.py
```

### 3. Commit Changes

```bash
# Commit with descriptive message
git commit -m "feat: Add SMS notification system

- Implement SMS gateway integration
- Add notification templates
- Add tests for SMS delivery
- Update documentation"

# Or use alias
git cm "feat: Add SMS notification system"
```

### 4. Push to Remote

```bash
# Push your branch
git push origin feature/your-feature-name

# Or set upstream and push (first time)
git push -u origin feature/your-feature-name
# Or use alias
git psu feature/your-feature-name
```

### 5. Create Pull Request

1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill in PR template
5. Request review
6. Address feedback
7. Merge when approved

### 6. After Merge

```bash
# Switch back to master
git checkout master

# Pull latest changes
git pull origin master

# Delete local feature branch
git branch -d feature/your-feature-name

# Delete remote feature branch (if not auto-deleted)
git push origin --delete feature/your-feature-name
```

## Commit Message Convention

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```bash
# Feature
git commit -m "feat(voice): Add voice biometric authentication"

# Bug fix
git commit -m "fix(session): Resolve session timeout race condition"

# Documentation
git commit -m "docs(api): Update API endpoint documentation"

# Test
git commit -m "test(content): Add property tests for content safety"

# Refactor
git commit -m "refactor(modules): Extract common module logic to base class"
```

## Useful Git Commands

### Viewing History

```bash
# Pretty log with graph
git log --oneline --graph --all --decorate
# Or use alias
git lg

# Show last commit
git log -1 HEAD --stat
# Or use alias
git last

# Show commits by author
git log --author="Your Name"

# Show commits in date range
git log --since="2 weeks ago"
```

### Undoing Changes

```bash
# Discard changes in working directory
git checkout -- filename

# Unstage file
git reset HEAD filename
# Or use alias
git unstage filename

# Amend last commit
git commit --amend
# Or use alias
git ca

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

### Stashing Changes

```bash
# Save current changes
git stash save "Work in progress on feature X"
# Or use alias
git ss "Work in progress on feature X"

# List stashes
git stash list
# Or use alias
git sl

# Apply most recent stash
git stash apply
# Or use alias
git sa

# Apply specific stash
git stash apply stash@{2}

# Drop stash
git stash drop stash@{0}
```

### Branch Management

```bash
# List all branches
git branch -v
# Or use alias
git br

# List remote branches
git branch -r

# Delete local branch
git branch -d feature/old-feature

# Delete remote branch
git push origin --delete feature/old-feature

# Rename current branch
git branch -m new-branch-name
```

### Syncing with Remote

```bash
# Fetch changes from remote
git fetch origin

# Pull changes (fetch + merge)
git pull origin master
# Or use alias
git pl

# Pull with rebase
git pull --rebase origin master

# Push changes
git push origin feature/your-branch
# Or use alias
git ps
```

## Resolving Merge Conflicts

### When Conflicts Occur

```bash
# Pull latest changes
git pull origin master

# If conflicts occur, Git will notify you
# Edit conflicted files manually
# Look for conflict markers:
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> branch-name

# After resolving conflicts
git add resolved-file.py
git commit -m "merge: Resolve conflicts with master"
```

### Preventing Conflicts

- Pull frequently from master
- Keep feature branches short-lived
- Communicate with team about overlapping work
- Use small, focused commits

## Git Aliases

Run the alias setup script:

```bash
# On Windows PowerShell
.\.git-aliases.ps1

# On Linux/Mac
bash .git-aliases.sh
```

Then use shortcuts like:
```bash
git st      # Instead of git status --short
git lg      # Instead of git log --oneline --graph --all
git co      # Instead of git checkout
git cm      # Instead of git commit -m
```

## Best Practices

### Do's ✅
- Commit frequently with clear messages
- Pull before starting new work
- Keep commits focused and atomic
- Write descriptive commit messages
- Test before committing
- Review your changes before committing
- Use branches for all changes
- Delete merged branches

### Don'ts ❌
- Don't commit sensitive data (credentials, keys)
- Don't commit large binary files
- Don't commit generated files
- Don't force push to shared branches
- Don't commit broken code
- Don't mix multiple changes in one commit
- Don't commit directly to master

## Troubleshooting

### Accidentally Committed to Master

```bash
# Create a branch from current state
git branch feature/my-changes

# Reset master to remote
git reset --hard origin/master

# Switch to your feature branch
git checkout feature/my-changes
```

### Need to Update Feature Branch with Latest Master

```bash
# On your feature branch
git checkout feature/your-branch

# Fetch latest changes
git fetch origin

# Rebase on master
git rebase origin/master

# If conflicts, resolve and continue
git add resolved-file.py
git rebase --continue

# Force push (only if branch not shared)
git push --force-with-lease origin feature/your-branch
```

### Accidentally Deleted Important Changes

```bash
# Find the commit hash
git reflog

# Restore from reflog
git checkout <commit-hash>

# Create a branch to save it
git checkout -b recovered-changes
```

## Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flight Rules](https://github.com/k88hudson/git-flight-rules)

## Questions?

If you have questions about the Git workflow:
1. Check this guide
2. Check CONTRIBUTING.md
3. Ask in team chat
4. Open an issue with "question" label

---

Happy coding! 🚀
