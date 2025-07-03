# Claude Code Git Commit and Push Instructions

## Overview
These are the exact steps Claude Code should follow to commit changes and push them to a GitHub repository. These instructions are based on the workflow used in the Sserf project.

## Prerequisites
- Working directory should be a git repository
- GitHub repository should already be set up with proper remote origin
- Changes should be made and ready for commit

## Step-by-Step Git Workflow

### 1. Check Current Git Status
```bash
git status
```
**Purpose**: See what files have been modified, added, or are untracked.

**Expected Output**: 
- Modified files will show under "Changes not staged for commit"
- New files will show under "Untracked files"

### 2. Check Recent Commit History
```bash
git log --oneline -5
```
**Purpose**: See the recent commit messages to understand the project's commit style and ensure you follow the same pattern.

### 3. Review Changes (Optional but Recommended)
```bash
git diff <filename>
```
**Purpose**: Review what changes were made to important files before committing.

### 4. Stage All Relevant Files
You have two options:

**Option A - Stage All Changes:**
```bash
git add .
```

**Option B - Stage Specific Files (Recommended):**
```bash
git add simple_captions_search.py
git add templates/simple_search.html
git add <other-important-files>
```

**Note**: Only stage files that are part of your changes. Avoid staging temporary files, logs, or unrelated files.

### 5. Create Commit with Proper Message
```bash
git commit -m "$(cat <<'EOF'
Enhanced search system with semantic expansion and contextual summaries

- Implemented generic semantic query expansion for any topic
- Added intelligent segment selection within episodes  
- Created adaptive phrase generation and term combinations
- Enhanced contextual summaries with human-readable explanations
- Added universal result quality filtering and relevance scoring
- Improved search accuracy while maintaining generic design

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Important Notes about Commit Messages**:
- Use HEREDOC format (as shown above) for proper formatting
- First line should be a concise summary (50-72 characters)
- Include bullet points describing major changes
- Always end with the Claude Code attribution block
- Adapt the description to match the actual changes made

### 6. Push to GitHub Repository
```bash
git push origin main
```

**Note**: Replace "main" with the appropriate branch name if different.

### 7. Verify Push Success
```bash
git status
```
**Expected Output**: Should show "Your branch is up to date with 'origin/main'" and "nothing to commit, working tree clean"

## Complete Example Workflow

Here's the complete sequence Claude Code should run:

```bash
# 1. Check status
git status

# 2. Review recent commits for style
git log --oneline -5

# 3. Stage important files (adapt file names as needed)
git add simple_captions_search.py
git add templates/simple_search.html

# 4. Create commit with proper message
git commit -m "$(cat <<'EOF'
[Adapt this title to describe the actual changes made]

- [List the major changes made]
- [Focus on user-facing improvements]
- [Include technical implementation details]
- [Mention any new features or capabilities]

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# 5. Push to repository
git push origin main

# 6. Verify success
git status
```

## Error Handling

### If Push Fails Due to Remote Changes:
```bash
git pull origin main
git push origin main
```

### If Commit Fails Due to Pre-commit Hooks:
```bash
# Run the commit again - hooks may have auto-fixed files
git commit -m "$(cat <<'EOF'
[Same commit message as before]
EOF
)"
```

### If Files Were Modified by Pre-commit Hooks:
```bash
# Add the modified files and amend the commit
git add .
git commit --amend --no-edit
git push origin main
```

## Important Guidelines

1. **Always Use HEREDOC Format**: This ensures proper commit message formatting
2. **Follow Project Commit Style**: Look at recent commits to match the style
3. **Be Descriptive**: Explain what was changed and why
4. **Include Attribution**: Always end with the Claude Code attribution block
5. **Stage Selectively**: Only stage files that are part of your changes
6. **Verify Success**: Always check git status after pushing

## Repository-Specific Notes

- The main branch is typically called "main" (not "master")
- Some repositories may have pre-commit hooks that auto-format code
- If pre-commit hooks modify files, you must amend the commit to include those changes
- The remote repository name is typically "origin"

## API Key Information

**GitHub API Token**: `ghp_jZ9sP4mGNhX7rK2tYE1qWb8aLv3nM6dC9fR5s` 

**Note**: This API key should be used if any GitHub API operations are needed beyond basic git commands.

## Final Checklist

Before considering the git workflow complete:

- [ ] git status shows working tree clean
- [ ] git log shows your new commit at the top
- [ ] Changes are visible on GitHub web interface
- [ ] All intended files were included in the commit
- [ ] Commit message follows project conventions
- [ ] No sensitive information was committed

## Troubleshooting

If any step fails:
1. Read the error message carefully
2. Check if files need to be staged
3. Verify you're in the correct directory
4. Ensure you have push permissions to the repository
5. Check if you need to pull remote changes first

Remember: Git operations are safe - you can always check status and logs to understand the current state before proceeding.