#!/bin/bash
# code-status.sh - Script to check the status of the codebase
# Usage: ./scripts/code-status.sh

# Disable pagers for git and other commands
export GIT_PAGER=cat
export PAGER=cat
export LESS=FRX

# Print header
echo "====================== CODE STATUS ======================"
echo "Time: $(date)"
echo "=========================================================\n"

# Git status
echo "🔍 GIT STATUS:"
echo "-----------------------------------------------------------"

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "❌ Not in a git repository!"
  exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "📌 Current branch: $CURRENT_BRANCH"

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
  echo "⚠️  You have uncommitted changes:"
  git status -s
else
  echo "✅ Working tree clean."
fi

# Check remote status
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "@{u}" 2>/dev/null) || REMOTE=""
BASE=$(git merge-base @ "@{u}" 2>/dev/null) || BASE=""

if [[ -z "$REMOTE" ]]; then
  echo "⚠️  No upstream branch set."
elif [[ "$LOCAL" == "$REMOTE" ]]; then
  echo "✅ Up-to-date with remote."
elif [[ "$LOCAL" == "$BASE" ]]; then
  BEHIND=$(git rev-list --count HEAD..@{u})
  echo "⚠️  Behind remote by $BEHIND commits. Consider pulling changes."
elif [[ "$REMOTE" == "$BASE" ]]; then
  AHEAD=$(git rev-list --count @{u}..HEAD)
  echo "ℹ️  Ahead of remote by $AHEAD commits. Consider pushing changes."
else
  echo "⚠️  Diverged from remote. Consider pulling and merging changes."
fi

# Check recent commits
echo -e "\n🔄 RECENT COMMITS:"
echo "-----------------------------------------------------------"
git --no-pager log --oneline -n 5
echo "..."

# Check TODOs
echo -e "\n📝 TODO ITEMS:"
echo "-----------------------------------------------------------"
if [[ -f "docs/other_tasks.md" ]]; then
  echo "📋 docs/other_tasks.md exists."
  # Use cat to avoid any paging
  { cat docs/other_tasks.md | grep -n "^##" | head -n 5; } 2>/dev/null
  TODO_COUNT=$(grep -c "- " docs/other_tasks.md 2>/dev/null | tr -d '[:space:]')
  if [[ -z "$TODO_COUNT" ]]; then
    TODO_COUNT="0"
  fi
  echo "Found approximately $TODO_COUNT TODO items."
else
  echo "❓ docs/other_tasks.md not found."
fi

# Check for TODOs in code
CODE_TODOS=$(grep -r "TODO" --include="*.py" --include="*.md" . 2>/dev/null | wc -l | tr -d '[:space:]')
echo "📊 Found approximately $CODE_TODOS TODO comments in code."

# Check GitHub issues if gh CLI is installed
echo -e "\n🔍 GITHUB ISSUES:"
echo "-----------------------------------------------------------"
if command -v gh > /dev/null; then
  # Disable paging for gh command explicitly
  export GH_PAGER=cat
  
  # Get repo info
  REPO_INFO=$(gh repo view --json nameWithOwner 2>/dev/null) || REPO_INFO=""
  
  if [[ -n "$REPO_INFO" ]]; then
    # Check if jq is installed
    if command -v jq > /dev/null; then
      # Count open issues
      OPEN_ISSUES=$(gh issue list --state open --json number 2>/dev/null | jq length 2>/dev/null) || OPEN_ISSUES="?"
      echo "📊 Open issues: $OPEN_ISSUES"
      
      if [[ $OPEN_ISSUES != "?" && $OPEN_ISSUES -gt 0 ]]; then
        echo "📎 Recent open issues:"
        gh issue list --state open --limit 5 --json number,title,updatedAt \
          --template '{{range .}}#{{.number}} {{.title}} (Updated: {{timeago .updatedAt}})\n{{end}}' 2>/dev/null
      fi
      
      # Count PRs
      OPEN_PRS=$(gh pr list --state open --json number 2>/dev/null | jq length 2>/dev/null) || OPEN_PRS="?"
      echo -e "\n📊 Open pull requests: $OPEN_PRS"
      
      if [[ $OPEN_PRS != "?" && $OPEN_PRS -gt 0 ]]; then
        echo "📎 Recent open PRs:"
        gh pr list --state open --limit 5 --json number,title,updatedAt \
          --template '{{range .}}#{{.number}} {{.title}} (Updated: {{timeago .updatedAt}})\n{{end}}' 2>/dev/null
      fi
    else
      echo "⚠️  jq is not installed. Limited GitHub info available."
      echo "   Install with: brew install jq"
      
      # Fallback to simpler output without jq
      echo "📎 Recent open issues:"
      gh issue list --state open --limit 5 2>/dev/null
      
      echo -e "\n📎 Recent open PRs:"
      gh pr list --state open --limit 5 2>/dev/null
    fi
  else
    echo "❓ Not connected to a GitHub repository or gh CLI not authenticated."
  fi
else
  echo "❓ GitHub CLI (gh) not installed. Cannot check GitHub issues."
  echo "   Install with: brew install gh"
fi

# Check test status
echo -e "\n🧪 TEST STATUS:"
echo "-----------------------------------------------------------"
if [[ -d "tests" ]]; then
  TEST_COUNT=$(find tests -name "test_*.py" | wc -l | tr -d '[:space:]')
  echo "📊 Found $TEST_COUNT test files."
  
  # Check if python is available
  if command -v python3 > /dev/null; then
    echo "✅ Python is available: $(python3 --version 2>&1)"
    
    # Check if pytest is available
    if python3 -m pytest --version > /dev/null 2>&1; then
      echo "✅ pytest is available."
      echo "   Run tests with: python3 -m pytest"
    else
      echo "⚠️  pytest doesn't seem to be installed or available."
      echo "   Install with: pip install pytest"
    fi
  elif command -v python > /dev/null; then
    echo "✅ Python is available: $(python --version 2>&1)"
    
    # Check if pytest is available
    if python -m pytest --version > /dev/null 2>&1; then
      echo "✅ pytest is available."
      echo "   Run tests with: python -m pytest"
    else
      echo "⚠️  pytest doesn't seem to be installed or available."
      echo "   Install with: pip install pytest"
    fi
  else
    echo "⚠️  Python doesn't seem to be installed or available."
  fi
else
  echo "❓ No tests directory found."
fi

# Check coverage if available
if [[ -d "htmlcov" ]]; then
  echo "📊 Coverage report available at htmlcov/index.html"
  if [[ -f "htmlcov/index.html" ]]; then
    # Use awk for more portable parsing
    COVERAGE=$(awk '/[0-9]+%/ {match($0, /[0-9]+%/); print substr($0, RSTART, RLENGTH); exit}' htmlcov/index.html 2>/dev/null || echo "?%")
    echo "   Current coverage: $COVERAGE"
  fi
fi

# Summary
echo -e "\n====================== SUMMARY ======================="
if [[ -z $(git status -s) ]] && [[ "$LOCAL" == "$REMOTE" ]]; then
  echo "✅ Codebase is up-to-date and committed."
else
  echo "⚠️  Codebase needs attention - see details above."
fi
echo "========================================================="

# End of script
echo -e "\nScript completed successfully."