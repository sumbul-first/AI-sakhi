#!/bin/bash
# Git Aliases for AI Sakhi Development
# Run this script to set up useful git aliases

echo "Setting up Git aliases for AI Sakhi..."

# Status and log aliases
git config --global alias.st 'status --short'
git config --global alias.lg 'log --oneline --graph --all --decorate'
git config --global alias.last 'log -1 HEAD --stat'

# Branch management
git config --global alias.br 'branch -v'
git config --global alias.co 'checkout'
git config --global alias.cob 'checkout -b'

# Commit aliases
git config --global alias.cm 'commit -m'
git config --global alias.ca 'commit --amend'
git config --global alias.unstage 'reset HEAD --'

# Diff aliases
git config --global alias.df 'diff'
git config --global alias.dfs 'diff --staged'

# Remote aliases
git config --global alias.pl 'pull'
git config --global alias.ps 'push'
git config --global alias.psu 'push -u origin'

# Stash aliases
git config --global alias.sl 'stash list'
git config --global alias.sa 'stash apply'
git config --global alias.ss 'stash save'

# Useful shortcuts
git config --global alias.contributors 'shortlog --summary --numbered'
git config --global alias.aliases 'config --get-regexp alias'

echo "Git aliases configured successfully!"
echo ""
echo "Available aliases:"
echo "  git st       - Short status"
echo "  git lg       - Pretty log graph"
echo "  git last     - Show last commit"
echo "  git br       - List branches"
echo "  git co       - Checkout"
echo "  git cob      - Checkout new branch"
echo "  git cm       - Commit with message"
echo "  git ca       - Amend last commit"
echo "  git unstage  - Unstage files"
echo "  git df       - Show diff"
echo "  git dfs      - Show staged diff"
echo "  git pl       - Pull"
echo "  git ps       - Push"
echo "  git psu      - Push and set upstream"
echo "  git sl       - List stashes"
echo "  git sa       - Apply stash"
echo "  git ss       - Save stash"
echo "  git contributors - Show contributors"
echo "  git aliases  - List all aliases"
