# CodexGUI - Installation and Usage Guide

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI Codex CLI installed and configured

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Usage

1. **Select a Task Template**: Choose from predefined templates like "File Organization", "Business Card Data Extraction", etc.

2. **Select Target Folder**: Click "Browse..." to select the folder you want to process

3. **Review/Edit Prompt**: The prompt will be automatically filled based on the template. You can customize it if needed.

4. **Execute**: Click "Execute Task" to run the Codex CLI with your prompt

5. **View Output**: Real-time output will be displayed in the output panel

## Available Templates

- **File Organization**: Organize files by type and date
- **Business Card Data Extraction**: Extract data from business card images
- **Code Analysis**: Analyze code structure and generate documentation
- **Receipt to Expense Report**: Extract data from receipts
- **Document Summary**: Summarize multiple documents
- **Photo Organization**: Organize photos by date and event
- **Code Review**: Review code and provide suggestions
- **Data Cleanup**: Clean and standardize data files
- **Meeting Notes Summary**: Summarize meeting notes

## Configuration

Templates are stored in `resources/templates.json`. You can edit this file to add your own custom templates.

## Troubleshooting

### Codex CLI Not Found

If you see a warning that Codex CLI is not available:

1. Ensure Codex CLI is installed: Follow OpenAI's installation guide
2. Check if `codex` command is in your PATH
3. Try running `codex --version` in terminal to verify

### Permission Errors

If you encounter permission errors when accessing folders:
- Ensure you have read/write permissions for the target folder
- On macOS, you may need to grant permissions in System Preferences

## License

MIT License - See LICENSE file for details
