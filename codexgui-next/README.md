# CodexGUI Next

Chat-driven GUI for ChatGPT API × Codex CLI integration.

## Overview

CodexGUI Next is a next-generation GUI application that combines ChatGPT API for planning and conversation with Codex CLI for local file operations. It provides a safe, user-friendly interface for organizing, creating, and modifying files.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   ChatGPT API   │◄───────►│  Orchestrator    │
│   (Planning)    │         │  (State Machine) │
└─────────────────┘         └──────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  Local Runner    │
                            │  (Codex CLI)     │
                            └──────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  File System     │
                            └──────────────────┘
```

## Features (M1)

- **Explorer Panel**: Tree view of target folder with file selection
- **Chat Panel**: Task cards and conversation interface
- **Detail Tab**: Raw logs (stdout/stderr, commands, events)
- **Stream Display**: Real-time output from Codex CLI
- **Cancel Support**: Kill running processes

## Data Transmission Policy

**Minimize data sent to OpenAI API:**
- ✅ Folder paths, file names (limited)
- ✅ File metadata (extension, size, date)
- ✅ Diff summaries, error messages (truncated)
- ❌ Source code content, confidential data, binary content

## Safety Design

All modification tasks require:
1. **Preview**: Show diffs before applying
2. **Confirmation**: Explicit user approval
3. **Backup**: Create timestamped backup
4. **Rollback**: Restore from backup if needed

## Project Structure

```
codexgui-next/
├── main.py              # Entry point
├── core/
│   ├── orchestrator.py  # State management
│   ├── openai_client.py # ChatGPT API integration
│   ├── runner.py        # Codex CLI executor
│   ├── result_parser.py # Parse and structure results
│   └── storage.py       # History, settings, API key
├── gui/
│   ├── main_window.py   # Main application window
│   ├── explorer_panel.py # File tree view
│   ├── chat_panel.py    # Chat and task cards
│   └── detail_panel.py  # Raw logs and events
└── resources/
    └── task_templates.json # Task card definitions
```

## Requirements

- Python 3.8+
- PySide6
- OpenAI Python SDK
- Codex CLI (installed and in PATH)

## Installation

```bash
cd codexgui-next
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Configuration

On first run, you'll be prompted to enter:
- OpenAI API Key
- Codex CLI path (auto-detected by default)
- Data transmission preferences

## Milestones

- **M1** (Current): UI layout, Runner streaming, Cancel support
- **M2**: Plan generation → Runner execution → Summary display
- **M3**: Modification tasks (diff preview → apply → backup → rollback)
- **M4**: History, re-execution, transmission policy, key management

## License

MIT License

## Author

garyohosu
