# Git Aliases for AI Sakhi Development (PowerShell)
# Run this script to set up useful git aliases

Write-Host "Setting up Git aliases for AI Sakhi..." -ForegroundColor Green

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

Write-Host "`nGit aliases configured successfully!" -ForegroundColor Green
Write-Host "`nAvailable aliases:" -ForegroundColor Yellow
Write-Host "  git st       - Short status"
Write-Host "  git lg       - Pretty log graph"
Write-Host "  git last     - Show last commit"
Write-Host "  git br       - List branches"
Write-Host "  git co       - Checkout"
Write-Host "  git cob      - Checkout new branch"
Write-Host "  git cm       - Commit with message"
Write-Host "  git ca       - Amend last commit"
Write-Host "  git unstage  - Unstage files"
Write-Host "  git df       - Show diff"
Write-Host "  git dfs      - Show staged diff"
Write-Host "  git pl       - Pull"
Write-Host "  git ps       - Push"
Write-Host "  git psu      - Push and set upstream"
Write-Host "  git sl       - List stashes"
Write-Host "  git sa       - Apply stash"
Write-Host "  git ss       - Save stash"
Write-Host "  git contributors - Show contributors"
Write-Host "  git aliases  - List all aliases"
