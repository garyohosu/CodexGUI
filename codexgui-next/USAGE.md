# CodexGUI Next - Usage Guide

Complete guide to using CodexGUI Next for safe, AI-powered file operations.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration](#configuration)
3. [Basic Operations](#basic-operations)
4. [Task Cards](#task-cards)
5. [Advanced Features](#advanced-features)
6. [Safety Features](#safety-features)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### First Launch

1. **Start the application**:
   ```bash
   cd codexgui-next
   python main.py
   ```

2. **Configure your API key**:
   - Go to File → Settings...
   - Enter your OpenAI API key
   - Click "Test Connection" to verify
   - Click "OK" to save

3. **Select a folder**:
   - Use the Explorer panel (left side)
   - Click to expand folders
   - Select your target folder

4. **Run your first task**:
   - Click "📄 Create/Update File List" card
   - Review the AI-generated plan
   - Click "Confirm" to execute
   - View the results in the chat

## Configuration

### API Settings

**Location**: File → Settings... → API Settings tab

- **OpenAI API Key**: Your personal API key from OpenAI
  - Get one at: https://platform.openai.com/api-keys
  - Stored securely in: `~/.codexgui-next/settings.json`
  - Click "👁️ Show" to reveal/hide the key
  - Click "Test Connection" to verify

### Transmission Policy

**Location**: File → Settings... → Transmission Policy tab

Controls what data is sent to OpenAI API:

- **Send File Content**: OFF by default (metadata only)
  - When OFF: Only file names, sizes, dates sent
  - When ON: File content may be sent (with limits below)
  
- **Max Files to Send**: Default 10
  - Limits the number of files analyzed
  - Protects against large folders
  
- **Max File Size**: Default 100 KB
  - Files larger than this are excluded
  - Prevents sending large binaries
  
- **Send Diff Content**: ON by default
  - Sends diff summaries for review (truncated)
  - Helps AI understand changes
  
- **Send Error Messages**: ON by default
  - Sends error logs to help AI debug
  - Truncated to protect sensitive info

**Recommendation**: Keep defaults for maximum privacy.

### Codex CLI Settings

**Location**: File → Settings... → Codex CLI Settings tab

- **Codex CLI Path**: Path to your Codex executable
  - Leave empty for auto-detection
  - Windows example: `C:\Program Files\Codex\codex.exe`
  - Linux/macOS example: `/usr/local/bin/codex`
  - Click "Browse..." to select file
  - Click "Test" to verify availability

**Note**: Codex CLI is optional. Many tasks work with standard shell commands.

## Basic Operations

### Selecting Folders

1. **Explorer Panel** (left side):
   - Tree view shows folder structure (3 levels deep)
   - Click folders to expand/collapse
   - Selected folder appears highlighted
   - Status bar shows: "対象フォルダ: /your/folder/path"

2. **Multi-Select Files** (for targeted operations):
   - Hold Ctrl (Windows/Linux) or Cmd (macOS)
   - Click individual files to select multiple
   - Status bar shows: "5 個のファイルを選択中" (5 files selected)

### Understanding the Interface

**Three Main Areas**:

1. **Explorer Panel (Left)**:
   - Browse and select folders/files
   - Shows folder structure
   - File count and total size displayed

2. **Chat Panel (Right)**:
   - 6 task cards at the top
   - Conversation log in the middle
   - Text input at the bottom

3. **Detail Panel (Bottom, toggleable)**:
   - View → Show Details to toggle
   - Shows real-time execution logs
   - Tabs: Chat Log / Detailed Logs / Event Log

### Workflow Steps

Every task follows this safe workflow:

```
1. Select Folder/Files
   ↓
2. Choose Task (click card or type request)
   ↓
3. AI Generates Plan
   ↓
4. Review Plan (safety check)
   ↓
5. Confirm Plan
   ↓
6. Background Execution
   ↓
7. AI Summarizes Results
   ↓
8. View Summary in Chat
```

## Task Cards

### 📁 Organize Folder

**Purpose**: Sort and organize files by type, date, or custom criteria

**Example Use Cases**:
- Organize downloads folder by file type
- Sort photos by date taken
- Group documents by project

**Workflow**:
1. Select messy folder
2. Click "Organize Folder" card
3. AI generates organization plan (e.g., create subfolders, move files)
4. Review and confirm
5. Files are organized automatically

**Safety**: Creates backup before moving files

---

### 📄 Create/Update File List

**Purpose**: Generate structured inventory of folder contents

**Example Use Cases**:
- Document project structure
- Create file manifest
- Export folder contents to text/CSV

**Workflow**:
1. Select folder to document
2. Click "Create/Update File List" card
3. AI generates list format (tree, table, etc.)
4. Confirm
5. File list created in folder

**Output Examples**:
- Tree structure: `file_tree.txt`
- CSV format: `file_inventory.csv`
- Markdown: `file_list.md`

---

### 🔍 Find Large Files

**Purpose**: Identify files consuming disk space

**Example Use Cases**:
- Free up disk space
- Find forgotten large downloads
- Identify bloat in projects

**Workflow**:
1. Select folder to scan
2. Click "Find Large Files" card
3. AI scans and identifies largest files
4. View results sorted by size
5. Decide what to delete/archive

**Customization**: Specify size threshold in custom request (e.g., "Find files larger than 50MB")

---

### 🔄 Find Duplicates

**Purpose**: Locate duplicate files (same content, different names/locations)

**Example Use Cases**:
- Remove duplicate photos
- Clean up redundant documents
- Merge duplicate backups

**Workflow**:
1. Select folder to scan
2. Click "Find Duplicates" card
3. AI scans using file hashes
4. View duplicate groups
5. Choose which copies to keep/delete

**Safety**: Never deletes automatically; you choose what to remove

---

### 📝 Create/Update README

**Purpose**: Generate or update project documentation

**Example Use Cases**:
- Document new project structure
- Update outdated README
- Create quick project overview

**Workflow**:
1. Select project folder
2. Click "Create/Update README" card
3. AI analyzes project structure and code
4. Generates comprehensive README
5. Review and approve
6. README.md created/updated

**Content Includes**:
- Project description
- File structure
- Installation instructions
- Usage examples

---

### 🔎 Review Changes

**Purpose**: Analyze recent file modifications

**Example Use Cases**:
- Review what changed in last commit
- Check recent edits before backup
- Audit folder activity

**Workflow**:
1. Select folder to review
2. Click "Review Changes" card
3. AI lists recently modified files
4. View change summary
5. Decide if changes are as expected

**Time Range**: Configurable (default: last 24 hours)

---

## Advanced Features

### Custom Requests

Instead of using task cards, type custom instructions:

**Examples**:
- "Find all Python files larger than 1MB"
- "Create a CSV listing all images with their dimensions"
- "Organize photos by year and month"
- "Find files modified in the last week"

**How to Use**:
1. Select target folder
2. Type custom request in input field
3. Press Enter or click "送信 ▶"
4. AI generates custom plan
5. Review and execute

### Multi-File Operations

Select specific files for targeted tasks:

1. **Select Files**:
   - Hold Ctrl/Cmd and click files in Explorer
   - Status bar shows count: "3 個のファイルを選択中"

2. **Run Task**:
   - Choose task card or type custom request
   - AI focuses only on selected files

**Example Use Cases**:
- Analyze only `.py` files in folder
- Organize selected photos only
- Generate list of specific documents

### Real-Time Logs

View detailed execution logs as they happen:

1. **Enable Detail Panel**:
   - View → Show Details
   - Or toggle with keyboard shortcut

2. **View Logs**:
   - **Chat Log Tab**: Conversation history
   - **Detailed Logs Tab**: stdout/stderr from Codex CLI
   - **Event Log Tab**: System events and status

3. **Use Cases**:
   - Debug task failures
   - Monitor long-running operations
   - Learn what commands are executed

### Cancel Execution

Stop a running task safely:

1. **During Execution**:
   - Status bar shows: "実行中..."
   - Click "Cancel" button (if available)
   - Or close application (prompts for confirmation)

2. **Behavior**:
   - Process is killed gracefully
   - Partial results are preserved
   - No data loss

## Safety Features

### Plan Review

**Every task requires plan review**:

1. AI generates plan
2. You see exactly what will happen:
   - Commands to be executed
   - Files to be modified
   - Expected outcomes
3. You explicitly approve or reject

**Example Plan**:
```
Plan: Organize files by type
Actions:
  1. Create folders: Images/, Documents/, Videos/
  2. Move 15 .jpg files to Images/
  3. Move 8 .pdf files to Documents/
  4. Move 3 .mp4 files to Videos/
Safety: Backup created before moving
```

### Minimal Data Transmission

**Default behavior**:
- Only folder paths and file metadata sent to OpenAI
- No source code or file content transmitted
- User controls exactly what is shared (Settings → Transmission Policy)

**What AI Sees**:
```json
{
  "folder": "/home/user/projects/myapp",
  "files": [
    {"name": "main.py", "size": 1024, "modified": "2026-01-15"},
    {"name": "README.md", "size": 512, "modified": "2026-01-14"}
  ]
}
```

**What AI Never Sees** (unless you enable it):
- Source code content
- File contents
- Sensitive data

### Backup & Rollback (M3)

**Coming in Milestone 3**:
- Automatic backups before modifications
- Timestamped backup folders
- One-click rollback if something goes wrong

**Example**:
```
Before modifying files:
  - Backup created: .codexgui_backup_20260115_143022/
  - If something breaks: Click "Rollback" to restore
```

## Troubleshooting

### Common Issues

#### "API key not configured"

**Solution**:
1. File → Settings...
2. API Settings tab
3. Enter your OpenAI API key
4. Click "Test Connection"
5. Click "OK" to save

---

#### "Codex CLI not found"

**Solution A** (Auto-detect):
1. Install Codex CLI system-wide
2. Ensure it's in your PATH
3. Restart application

**Solution B** (Manual path):
1. File → Settings...
2. Codex CLI Settings tab
3. Browse to Codex executable
4. Click "Test" to verify
5. Click "OK" to save

---

#### "Task failed to execute"

**Debugging**:
1. Enable detail panel: View → Show Details
2. Check "Detailed Logs" tab for error messages
3. Common causes:
   - Insufficient permissions
   - Codex CLI not installed
   - Invalid folder path
4. Fix issue and retry

---

#### "No response from OpenAI"

**Checks**:
1. Verify internet connection
2. Test API key: Settings → API Settings → Test Connection
3. Check API key has credits: https://platform.openai.com/usage
4. Check OpenAI status: https://status.openai.com/

---

#### Application is slow

**Possible Causes**:
1. **Large folder**: Scanning thousands of files takes time
   - Solution: Select smaller subfolders
2. **OpenAI API rate limits**: Too many requests
   - Solution: Wait a minute and retry
3. **Background execution**: Heavy Codex CLI operations
   - Solution: View logs to monitor progress

---

### Getting Help

**Resources**:
- GitHub Issues: https://github.com/garyohosu/CodexGUI/issues
- OpenAI Documentation: https://platform.openai.com/docs
- Codex CLI Docs: https://developers.openai.com/codex/cli

**Before Reporting Bugs**:
1. Enable detail panel
2. Copy full error message from "Detailed Logs" tab
3. Include:
   - Operating system
   - Python version
   - Error message
   - Steps to reproduce

## Keyboard Shortcuts

*Coming in future releases*

## Language Support

**Available Languages**:
- English (en)
- Japanese (ja)

**Switch Language**:
1. File → Language
2. Select language
3. Application restarts with new language

**Add New Language**:
1. Copy `i18n/en.json` to `i18n/yourlang.json`
2. Translate all strings
3. Restart application
4. New language appears in menu

## Tips & Best Practices

1. **Start Small**: Test tasks on small folders first
2. **Review Plans**: Always read AI-generated plans before confirming
3. **Enable Logs**: Turn on detail panel for transparency
4. **Backup Important Data**: Use separate backup before major operations
5. **Custom Requests**: Be specific in your requests for better results
6. **Transmission Policy**: Keep default settings for privacy
7. **API Credits**: Monitor your OpenAI usage to avoid surprises

## What's Next?

**Upcoming Features**:
- **M3**: Diff preview, backup, rollback
- **M4**: Execution history, re-run tasks, advanced key management

**Stay Updated**:
- Watch the GitHub repository: https://github.com/garyohosu/CodexGUI
- Check CHANGELOG.md for new features

---

**Happy organizing with CodexGUI Next! 🚀**
