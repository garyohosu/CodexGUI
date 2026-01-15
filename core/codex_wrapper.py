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
            # Build command - Use 'exec' for non-interactive execution
            # Options must come before the prompt
            cmd = [self.codex_path, "exec", "-q", prompt]
            
            # Set working directory
            cwd = working_dir or os.getcwd()
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
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
        callback=None
    ):
        """
        Execute a prompt with streaming output.
        
        Args:
            prompt: The prompt to execute
            working_dir: Working directory for execution
            callback: Callback function for streaming output (receives output line)
        """
        try:
            # Build command - Use 'exec' for non-interactive execution
            # Options must come before the prompt
            cmd = [self.codex_path, "exec", "-q", prompt]
            cwd = working_dir or os.getcwd()
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
                bufsize=1
            )
            
            # Stream stdout and stderr
            if callback:
                # Read from both stdout and stderr
                import select
                import sys
                
                while True:
                    # Read available lines
                    line = process.stdout.readline()
                    if line:
                        callback(line.rstrip())
                    
                    # Check if process finished
                    if process.poll() is not None:
                        # Read remaining output
                        for line in process.stdout:
                            callback(line.rstrip())
                        break
            
            # Wait for completion
            process.wait()
            
            # Get any remaining stderr
            stderr = process.stderr.read()
            
            return CodexResult(
                success=process.returncode == 0,
                output="",  # Already streamed via callback
                error=stderr,
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
            return (
                "Codex CLI is not installed or not in PATH.\n\n"
                "To install Codex CLI on Windows:\n"
                "1. Visit: https://developers.openai.com/codex/cli\n"
                "2. Download the Windows installer\n"
                "3. Run the installer\n"
                "4. Restart this application\n\n"
                "Expected executable names: codex.exe, codex.cmd"
            )
        else:
            return (
                "Codex CLI is not installed or not in PATH.\n\n"
                "To install Codex CLI:\n"
                "1. Visit: https://developers.openai.com/codex/cli\n"
                "2. Follow installation instructions\n"
                "3. Ensure 'codex' is in your PATH\n"
                "4. Restart this application"
            )


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
