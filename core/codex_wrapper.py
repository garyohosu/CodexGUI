"""
Codex CLI Wrapper Module

This module provides a Python interface to execute OpenAI Codex CLI commands
and retrieve results.
"""

import subprocess
import json
import os
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
    
    def __init__(self, codex_path: str = "codex"):
        """
        Initialize Codex wrapper.
        
        Args:
            codex_path: Path to codex CLI executable (default: "codex")
        """
        self.codex_path = codex_path
        self._check_codex_available()
    
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
            # Build command
            cmd = [self.codex_path, "prompt", prompt]
            
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
            cmd = [self.codex_path, "prompt", prompt]
            cwd = working_dir or os.getcwd()
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
                bufsize=1
            )
            
            # Stream stdout
            if callback:
                for line in process.stdout:
                    callback(line.rstrip())
            
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
        return self._check_codex_available()


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
