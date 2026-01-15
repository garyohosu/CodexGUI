# CodexGUI v0.0.1

A Qt/PySide6 GUI wrapper for OpenAI Codex CLI, enabling easy access to AI-powered code analysis, file organization, and task automation through an intuitive desktop interface.

## Motivation

After reading about Claude Code Work, I realized that many people find CLI (Command Line Interface) intimidating. This GUI wrapper makes Codex CLI accessible to everyone, regardless of their command-line experience.

## Overview

CodexGUI provides a user-friendly graphical interface for OpenAI's Codex CLI, making it easy to leverage AI-powered coding assistance without needing to work directly in the terminal.

## Features

- **Task Templates**: Pre-configured templates for common tasks like file organization, code analysis, and data extraction
- **Folder Selection**: Easy folder picker for selecting target directories
- **Real-time Output**: Live display of Codex CLI execution results
- **Execution History**: Keep track of previous tasks and prompts
- **Cross-platform**: Built with Qt/PySide6 for Windows, macOS, and Linux support

## Architecture

```
PySide6 GUI
    ↓
subprocess.run()
    ↓
codex CLI (with prompt arguments)
    ↓
Local file operations
```

## Requirements

- Python 3.8+
- PySide6
- OpenAI Codex CLI installed and configured

## Installation

Coming soon...

## Usage

Coming soon...

## Project Structure

```
CodexGUI/
├── main.py              # Entry point
├── gui/
│   ├── main_window.py   # Main window
│   ├── task_panel.py    # Task selection panel
│   └── output_panel.py  # Output display panel
├── core/
│   ├── codex_wrapper.py # Codex CLI execution wrapper
│   └── templates.py     # Prompt templates
├── resources/
│   └── templates.json   # Task template definitions
└── requirements.txt
```

## Use Cases

- **File Organization**: Automatically organize downloads, documents, and media files
- **Code Analysis**: Analyze codebases and generate documentation
- **Data Extraction**: Extract information from images, documents, and structured files
- **Task Automation**: Automate repetitive file management tasks

## License

MIT License

## Author

Created by garyohosu

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
