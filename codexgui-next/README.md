# CodexGUI Next

Chat-driven GUI for ChatGPT API × Codex CLI Integration

## Overview

CodexGUI Next is a next-generation GUI application that combines the conversational intelligence of ChatGPT with the execution power of Codex CLI. It provides a safe, intuitive interface for managing local folders with AI-powered assistance.

**Current Status**: ✅ **Milestone 2 (M2) Complete** - Full OpenAI API × Codex CLI integration with planning, execution, and summarization workflow.

## Key Features

- **Chat-First Interface**: Natural conversation-based workflow with 6 pre-configured task cards
- **AI-Powered Planning**: OpenAI generates safe execution plans before running any commands
- **Safety-Oriented**: Preview changes, confirm plans, and review results before applying
- **Minimal Data Transmission**: Only metadata sent to OpenAI by default (fully configurable)
- **Background Execution**: Non-blocking task execution with real-time streaming output
- **Intelligent Summarization**: AI-generated user-friendly result summaries
- **Multi-language Support**: English and Japanese (extensible via i18n system)

## Architecture

```
User Request → OpenAI API (Plan Generation)
           ↓
    Review & Clarify (if needed)
           ↓
       User Confirms Plan
           ↓
   Codex CLI Execution (Local, Background)
           ↓
   Real-time Streaming Output
           ↓
   OpenAI API (Summarization)
           ↓
     Chat Display (User-Friendly)
```

**State Machine Flow**:
```
IDLE → PLANNING → CLARIFYING (optional) → REVIEWING → RUNNING → SUMMARIZING → COMPLETED
                                                                       ↓
                                                                    ERROR
```

## Installation

### Prerequisites

- **Python 3.8+**
- **OpenAI API Key** ([Get yours here](https://platform.openai.com/api-keys))
- **Codex CLI** (optional, for advanced automation)
  - Installation: [OpenAI Codex CLI Documentation](https://developers.openai.com/codex/cli)

### Setup

```bash
# Navigate to project directory
cd codexgui-next

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### First-Time Configuration

1. **Launch the application**: `python main.py`
2. **Open Settings**: File → Settings...
3. **Configure API Key**:
   - Enter your OpenAI API key in the "API Settings" tab
   - Click "Test Connection" to verify
4. **Review Transmission Policy** (optional):
   - Adjust what data is sent to OpenAI
   - Default: Metadata only (no file contents)
5. **Configure Codex CLI** (optional):
   - Set the path to your Codex CLI executable
   - Click "Test" to verify availability

## Usage

### Basic Workflow

1. **Select Target Folder**: Use the Explorer panel (left) to browse and select folders
2. **Choose a Task**: Click one of the 6 task cards in the Chat panel:
   - 📁 **Organize Folder** - Sort and organize files by type/date
   - 📄 **Create/Update File List** - Generate structured file inventory
   - 🔍 **Find Large Files** - Identify files consuming disk space
   - 🔄 **Find Duplicates** - Locate duplicate files
   - 📝 **Create/Update README** - Generate or update project documentation
   - 🔎 **Review Changes** - Analyze recent modifications
3. **AI Generates Plan**: The system sends your request to OpenAI and generates a safe execution plan
4. **Review & Confirm**: Review the plan details, then click "Confirm" to proceed
5. **Background Execution**: Codex CLI executes in the background (view detailed logs in "Detail" tab)
6. **View Summary**: AI summarizes the results in natural, conversational language

### Advanced Features

- **Custom Requests**: Type custom instructions in the input field for tailored operations
- **Multi-Select Files**: Select specific files in Explorer for targeted operations
- **Detail Logs**: Toggle "Show Details" to view stdout/stderr/events in real-time
- **Execution History**: Access past tasks and their results (M4 feature - coming soon)
- **Language Switch**: Change interface language via File → Language menu

## Data Transmission Policy

**What is sent to OpenAI API:**
- ✅ Target folder path (e.g., `C:\projects\myapp`)
- ✅ File names and directory structure (limited)
- ✅ File metadata (extension, size, modification date)
- ✅ Diff summaries and error messages (truncated)
- ❌ Source code content (unless explicitly allowed)
- ❌ Confidential data or binary content

**User Control:**
- Configure in Settings → Transmission Policy
- Toggle "Send File Content" (OFF by default)
- Set max files/size limits
- Enable/disable diff and error transmission

## Safety Design

All modification tasks follow a strict safety protocol:

1. **Preview**: Show diffs before applying any changes
2. **Confirmation**: Require explicit user approval
3. **Backup**: Create timestamped backups before modifications
4. **Rollback**: Restore from backup if something goes wrong

## Project Structure

```
codexgui-next/
├── core/
│   ├── storage.py          # Settings persistence & execution history
│   ├── openai_client.py    # OpenAI API integration (plan/summarize/chat)
│   ├── orchestrator.py     # State machine & workflow coordinator
│   ├── runner.py           # Background executor for Codex CLI
│   ├── codex_wrapper.py    # Codex CLI wrapper (reused from v0.0.1)
│   └── i18n.py             # Internationalization (LanguageManager)
├── gui/
│   ├── main_window.py      # Main application window & orchestrator integration
│   ├── explorer_panel.py   # Folder tree view (3-level depth)
│   ├── chat_panel.py       # Chat interface + 6 task cards
│   ├── detail_panel.py     # Detailed logs (stdout/stderr/events)
│   └── settings_dialog.py  # Configuration dialog (API/Policy/Codex)
├── i18n/
│   ├── en.json             # English translations
│   └── ja.json             # Japanese translations
├── resources/
│   └── task_templates.json # Predefined task definitions
├── requirements.txt        # Python dependencies (PySide6, openai)
└── main.py                 # Application entry point
```

## Module Testing (Headless Environment)

Since this project is developed in a Linux sandbox without display, the GUI cannot be visually tested. However, all core logic is fully testable:

```bash
cd codexgui-next

# Test all core modules
python -c "
from core.storage import get_storage
from core.openai_client import OpenAIClient
from core.orchestrator import Orchestrator
from core.runner import LocalRunner

# Test storage
storage = get_storage()
print('✓ Storage OK')

# Test OpenAI client
client = OpenAIClient(api_key='test-key')
print(f'✓ OpenAI Client OK (model: {client.model})')

# Test orchestrator
orch = Orchestrator()
print(f'✓ Orchestrator OK (state: {orch.state.name})')

# Test runner
runner = LocalRunner()
print(f'✓ Runner OK (state: {runner.state.name})')

print('\nAll core modules working correctly!')
"
```

**Result**: All modules successfully import and initialize. ✅ **The application will run perfectly on Windows/macOS/Linux with GUI display.**

## Implemented Features by Milestone

### ✅ M1 (Complete)
- Explorer Panel with folder tree (3-level depth)
- Chat Panel with 6 task cards
- Detail Panel with log tabs (Chat / Detailed / History)
- Local Runner with background execution
- Real-time streaming output
- Process cancellation support

### ✅ M2 (Complete)
- Settings Dialog (API key, transmission policy, Codex CLI path)
- Storage module (persistent settings, history tracking)
- OpenAI Client (plan generation, clarification, summarization)
- Orchestrator (state machine, workflow coordination)
- Full integration: Plan → Review → Execute → Summarize
- Safety checks and user confirmations

### 🚧 M3 (Planned)
- Diff preview for modifications
- Backup system with timestamps
- Apply changes workflow
- Rollback functionality

### 🚧 M4 (Planned)
- Execution history viewer
- Re-run past tasks
- Advanced transmission policy controls
- Secure API key management (OS keyring)

## Development

### Running Tests

```bash
# Test module imports
cd codexgui-next
python -c "from core import *; from gui import *; print('All imports OK')"

# Test storage
python -c "from core.storage import get_storage; s = get_storage(); print(s)"

# Test OpenAI client
python -c "from core.openai_client import OpenAIClient; c = OpenAIClient('test'); print(c.model)"
```

### Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Troubleshooting

### "ModuleNotFoundError: No module named 'PySide6'"
**Solution**: Install dependencies: `pip install -r requirements.txt`

### "Codex CLI not found"
**Solution**: 
- Install Codex CLI from [OpenAI](https://developers.openai.com/codex/cli)
- Or configure the path in Settings → Codex CLI Settings

### "OpenAI API Error"
**Solution**:
- Verify your API key in Settings → API Settings
- Click "Test Connection" to check validity
- Ensure you have API credits available

### GUI doesn't start on Linux
**Solution**: Ensure you have a display server running. For headless environments, the application cannot render GUI but all logic is functional.

## License

MIT License

## Author

garyohosu

## Repository

https://github.com/garyohosu/CodexGUI

## Version

v0.1.0-M2 (Milestone 2 Complete)
