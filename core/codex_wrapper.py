"""
Codex CLI Wrapper Module

This module provides a Python interface to execute OpenAI Codex CLI commands
and retrieve results.
"""

import subprocess
import json
import os
import sys
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from core.i18n import tr


@dataclass
class CodexResult:
    """Result from Codex CLI execution."""
    success: bool
    output: str
    error: str
    exit_code: int


class CodexWrapper:
    """Wrapper for OpenAI Codex CLI."""
    
    def __init__(self, codex_path: Optional[str] = None):
        """
        Initialize Codex wrapper.
        
        Args:
            codex_path: Path to codex CLI executable (default: auto-detect)
        """
        self.codex_path = codex_path or self._find_codex_executable()
        self._available = self._check_codex_available()
    
    def _find_codex_executable(self) -> str:
        """
        Find Codex CLI executable in system.
        
        Returns:
            Path to codex executable
        """
        # Try common names
        if sys.platform == "win32":
            # Windows: try .exe and .cmd
            candidates = ["codex.exe", "codex.cmd", "codex"]
        else:
            # Unix-like: just codex
            candidates = ["codex"]
        
        # Check if in PATH
        for candidate in candidates:
            if shutil.which(candidate):
                return candidate
        
        # Return default
        return "codex.exe" if sys.platform == "win32" else "codex"
    
    def _check_codex_available(self) -> bool:
        """
        Check if Codex CLI is available in the system.
        
        Returns:
            True if Codex CLI is available, False otherwise
        """
        try:
            result = subprocess.run(
                [self.codex_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def execute_prompt(
        self,
        prompt: str,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = 300
    ) -> CodexResult:
        """
        Execute a prompt using Codex CLI.
        
        Args:
            prompt: The prompt to execute
            working_dir: Working directory for execution (default: current directory)
            timeout: Timeout in seconds (default: 300)
        
        Returns:
            CodexResult containing execution results
        """
        try:
            # Build command - Use 'exec' with --yolo for full automation
            # --yolo enables complete non-interactive execution without prompts
            # --skip-git-repo-check allows execution in non-git directories
            cmd = [
                self.codex_path, 
                "exec",
                "--yolo",                    # Full automation mode
                "--skip-git-repo-check",     # Allow non-git directories
                prompt
            ]
            
            # Set working directory
            cwd = working_dir or os.getcwd()
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                encoding='utf-8',      # Force UTF-8 encoding
                errors='replace'       # Replace invalid characters
            )
            
            return CodexResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return CodexResult(
                success=False,
                output="",
                error=f"Execution timed out after {timeout} seconds",
                exit_code=-1
            )
        except Exception as e:
            return CodexResult(
                success=False,
                output="",
                error=f"Error executing Codex CLI: {str(e)}",
                exit_code=-1
            )
    
    def execute_prompt_streaming(
        self,
        prompt: str,
        working_dir: Optional[str] = None,
        callback=None,
        timeout: Optional[int] = 300
    ):
        """
        Execute a prompt with streaming output.
        
        Args:
            prompt: The prompt to execute
            working_dir: Working directory for execution
            callback: Callback function for streaming output (receives output line)
            timeout: Timeout in seconds (default: 300)
        """
        try:
            # Build command - Use 'exec' with --yolo for full automation
            # --yolo enables complete non-interactive execution without prompts
            # --skip-git-repo-check allows execution in non-git directories
            cmd = [
                self.codex_path, 
                "exec",
                "--yolo",                    # Full automation mode
                "--skip-git-repo-check",     # Allow non-git directories
                prompt
            ]
            cwd = working_dir or os.getcwd()
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr to stdout
                text=True,
                cwd=cwd,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',          # Force UTF-8 encoding
                errors='replace'           # Replace invalid characters
            )
            
            # Stream output with timeout
            import threading
            import time
            
            output_lines = []
            error_occurred = False
            
            def read_output():
                nonlocal error_occurred
                try:
                    for line in iter(process.stdout.readline, ''):
                        if line:
                            output_lines.append(line.rstrip())
                            if callback:
                                callback(line.rstrip())
                except Exception as e:
                    error_occurred = True
                    if callback:
                        callback(f"Error reading output: {e}")
            
            # Start reading thread
            reader_thread = threading.Thread(target=read_output, daemon=True)
            reader_thread.start()
            
            # Wait for process with timeout
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                return CodexResult(
                    success=False,
                    output='\n'.join(output_lines),
                    error=f"Execution timed out after {timeout} seconds",
                    exit_code=-1
                )
            
            # Wait for reader thread to finish (with timeout)
            reader_thread.join(timeout=5)
            
            return CodexResult(
                success=process.returncode == 0,
                output='\n'.join(output_lines),
                error="" if not error_occurred else "Error occurred during output reading",
                exit_code=process.returncode
            )
            
        except Exception as e:
            return CodexResult(
                success=False,
                output="",
                error=f"Error during streaming execution: {str(e)}",
                exit_code=-1
            )
    
    def get_version(self) -> Optional[str]:
        """
        Get Codex CLI version.
        
        Returns:
            Version string or None if unavailable
        """
        try:
            result = subprocess.run(
                [self.codex_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None
    
    def is_available(self) -> bool:
        """
        Check if Codex CLI is available.
        
        Returns:
            True if available, False otherwise
        """
        return self._available
    
    def get_installation_help(self) -> str:
        """
        Get help message for installing Codex CLI.
        
        Returns:
            Installation help message
        """
        if sys.platform == "win32":
            return tr("codex.install_help_windows")
        else:
            return tr("codex.install_help_unix")


# Module-level convenience function
def execute_codex_prompt(prompt: str, working_dir: Optional[str] = None) -> CodexResult:
    """
    Convenience function to execute a Codex prompt.
    
    Args:
        prompt: The prompt to execute
        working_dir: Working directory for execution
    
    Returns:
        CodexResult containing execution results
    """
    wrapper = CodexWrapper()
    return wrapper.execute_prompt(prompt, working_dir)
